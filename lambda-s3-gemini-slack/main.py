import google.generativeai as genai
import json
import os
import re
import requests
import boto3
from datetime import datetime, timedelta
import pytz

def parse_gpt_text(text):
    # 각 제목과 내용을 추출하는 정규식
    pattern = r"\*\*제목 \d+: (.*?)\*\*\n(.*?)(https?://[^\s]+)"
    matches = re.findall(pattern, text, re.DOTALL)

    summary_data = []
    for match in matches:
        title = match[0].strip()
        content = match[1].strip()
        url = match[2].strip()
        
        summary_data.append({
            "title": title,
            "content": content,
            "url": url
        })
    
    return summary_data

def format_for_slack(summary_data):
    attachments = []
    for item in summary_data:
        title = item.get("title", "")
        content = item.get("content", "")
        url = item.get("url", "")
        
        # 슬랙 메시지 형식으로 변환
        attachment = {
            "color": "#36a64f",  # 첨부 메시지의 색상 코드 (초록색)
            "title": f"*{title}*",  # 제목을 굵게 표시
            "text": f"{content}\n<{url}|원본 링크>",  # 내용과 링크를 함께 표시
            "mrkdwn_in": ["text", "pretext"]  # 마크다운 적용
        }
        attachments.append(attachment)
    
    return attachments

def send_llm(data, date):
	genai.configure(api_key=os.environ['googleApiKey'])

	try:
		model = genai.GenerativeModel('gemini-1.5-flash')
		response = model.generate_content(f"입력 값 형식: title과 content, url로 이루어진 딕셔너리 형태인 데이터. 입력 값: {data}. 가공 처리: 주요 내용 요약 정리 자잘한 이야기는 넘어가도 괜찮. 출력 값 형식: 주요 내용 제목 1:  제목 1 관련된 내용 [링크]")
		summary_data = parse_gpt_text(response.text)
		formatted_attachments = format_for_slack(summary_data)
		
		# Slack 웹훅에 전송할 데이터 구성
		url = os.environ['webhook']
		header = {'Content-type': 'application/json'}
		icon_emoji = ":slack:"
		username = "DC 웹소설 연재 갤러리"

		slack_data = {
			"username": username,
			"attachments": formatted_attachments,
			"icon_emoji": icon_emoji
		}

		response = requests.post(url, headers=header, json=slack_data)
		if response.status_code != 200:
			raise Exception(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
	except Exception as e:
		print(f"Error sending message to Slack: {e}")

def handler(event, context):
	# S3 클라이언트 생성
	s3 = boto3.client('s3')

	# 이벤트에서 버킷 이름과 객체 키 가져오기
	bucket_name = event['Records'][0]['s3']['bucket']['name']
	object_key = event['Records'][0]['s3']['object']['key']

	print(f"Bucket: {bucket_name}, Object Key: {object_key}")
	# 현재 서울 시간 가져오기
	seoul_tz = pytz.timezone('Asia/Seoul')
	now = datetime.now(seoul_tz)

	# 하루 전 시간 계산
	previous_day = now - timedelta(days=1)
	target_date = previous_day.strftime('%Y-%m-%d')

	# 하루 전 파일의 접두사(prefix) 설정
	prefix = f'dc/{target_date}_'
	response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

	json_data = []
	
	if 'Contents' in response:
		for obj in response['Contents']:
			file_key = obj['Key']

			# 파일 내용 가져오기
			file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
			file_content = file_obj['Body'].read().decode('utf-8')
			json_data.append(json.loads(file_content))

	# JSON 데이터 처리
	send_llm(json_data, target_date)  # 이 부분은 데이터를 처리하는 함수라고 가정하고 있습니다.

	return {
		'statusCode': 200,
		'body': json.dumps(f"Processed files: {target_date}")
	}
	
if __name__ == '__main__':
    handler()