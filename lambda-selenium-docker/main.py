from datetime import datetime, timedelta
import json
import time
import pytz
import boto3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 시간 설정
seoul_tz = pytz.timezone('Asia/Seoul')
now = datetime.now(seoul_tz)
one_hour_ago = now - timedelta(hours=1)

# 언더플로우 처리: 0시에서 1시간 전은 전날 23시
if one_hour_ago.hour == 23 and now.hour == 0:
    today = (now - timedelta(days=1)).strftime('%Y-%m-%d')
else:
    today = one_hour_ago.strftime('%Y-%m-%d')

target_time = one_hour_ago.strftime('%H')

# S3 설정
s3 = boto3.client('s3')
bucket_name = 'crawling-data-save'  # S3 버킷 이름
file_name = f'dc/{today}_{target_time}.json'  # S3에 저장될 파일 이름

def handler(event=None, context=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/opt/chrome/chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
    chrome_options.add_argument('window-size=1392x1150')
    chrome_options.add_argument("disable-gpu")

    service = Service(executable_path="/opt/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    result_data = []
    try:
        for i in range(1, 4):
            driver.get(f"https://gall.dcinside.com/mgallery/board/lists/?id=tgijjdd&page={i}")
            elements = driver.find_elements(By.CSS_SELECTOR, "tbody.listwrap2 tr")

            for index in range(len(elements)):
                elements = driver.find_elements(By.CSS_SELECTOR, "tbody.listwrap2 tr")
                element = elements[index]
                
                data_type = element.get_attribute('data-type')
                date_title = element.find_element(By.CLASS_NAME, 'gall_date').get_attribute('title')
                date_time_parts = date_title.split(' ')
                date = date_time_parts[0]
                
                # 1시간 전의 날짜와 시간이 일치하는 글만 필터링
                if (data_type != "icon_notice" and data_type is not None) and date == today and date_time_parts[1][:2] == target_time:
                    # 게시물 링크 가져오기
                    url = element.find_element(By.TAG_NAME, "a").get_attribute('href')    

                    element.find_element(By.CSS_SELECTOR, "td.gall_tit.ub-word > a").click()
                    ele = driver.find_element(By.CSS_SELECTOR, "div.write_div")
                    title = driver.find_element(By.CSS_SELECTOR, "span.title_subject")
                    result_data.append({
                        "title": title.text,
                        "content": ele.text,
                        "url": url
                    })
                    driver.back()
            time.sleep(5)
        driver.quit()

        # JSON 데이터를 S3에 저장
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(result_data, ensure_ascii=False),
            ContentType='application/json'
        )

        return {
        "statusCode": 200,
        "body": json.dumps({
                "message": f"Crawling completed at {today+ ' ' + target_time + ':00'}",
                "s3_file_name": file_name
        }, ensure_ascii=False),}
    except Exception as e:
        driver.quit()
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Crawling Failed at {today+ ' ' + target_time + ':00'}",
                "error": str(e),
            }),
        }

if __name__ == '__main__':
    handler()
