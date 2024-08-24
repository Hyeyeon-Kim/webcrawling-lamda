import google.generativeai as genai
import json
import os
import requests
import boto3
from datetime import datetime, timedelta
import pytz

def send_llm(data):
	genai.configure(api_key=os.environ['googleApiKey'])

	try:
		model = genai.GenerativeModel('gemini-1.5-flash')
		response = model.generate_content(f"각 배열의 요소가 title과 content, url로 이루어진 딕셔너리 형태인 데이터를 넘겨주었을 때 주요 내용을 요약 정리해서 알려주고 각 타이틀에 맞는 원본 링크를 함께 첨부해줘 {data}")

		text = response.text
		# Slack 웹훅에 전송할 데이터 구성
		url = os.environ['webhook']
		header = {'Content-type': 'application/json'}
		icon_emoji = ":slack:"
		username = "DC 웹소설 연재 갤러리"
		attachments = [{
			"color": "good",
			"text": text  # 생성된 텍스트를 Slack으로 전송
		}]
		slack_data = {"username": username, "attachments": attachments, "icon_emoji": icon_emoji}
		requests.post(url, headers=header, json=slack_data)
	except Exception as e:
		print(f"Error generating text: {e}")

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

	# 1시간 전 시간 계산
	one_hour_ago = now - timedelta(hours=1)

	# 언더플로우 처리: 0시에서 1시간 전은 전날 23시로 설정
	if one_hour_ago.hour == 23 and now.hour == 0:
		target_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
	else:
		target_date = one_hour_ago.strftime('%Y-%m-%d')

	target_hour = one_hour_ago.strftime('%H')

	# 예상되는 파일 이름 생성 (예: "dc crawling_data_YYYY-MM-DD_HH.json")
	expected_file_key = f'dc/{target_date}_{target_hour}.json'
	# expected_file_key = "hello"

	try:
		# 예상된 파일 읽기
		file_obj = s3.get_object(Bucket=bucket_name, Key=expected_file_key)
		file_content = file_obj['Body'].read().decode('utf-8')
		json_data = json.loads(file_content)
		send_llm(json_data)
		return {
			'statusCode': 200,
			'body': json.dumps(f"Processed file: {expected_file_key}")
		}

	except s3.exceptions.NoSuchKey:
		# 파일이 존재하지 않을 때의 처리
		return {
			'statusCode': 404,
			'body': json.dumps(f"No file found for {expected_file_key}")
		}
	
if __name__ == '__main__':
    handler()