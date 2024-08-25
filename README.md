## 크롤링 전체 아키텍쳐
![크롤링 전체 아키텍쳐](https://cdn.discordapp.com/attachments/793022818757509131/1276880093188325388/2024-08-23_9.47.02.png?ex=66cb22c1&is=66c9d141&hm=d04c2ac33b726ac27998d64f9819e59a95ac2adec4a97b197a047278d5f18ba6&)

### lambda-selenium-docker: 
- 웹 사이트에서 글을 크롤링한 후 s3에 저장하는 람다
- aws 이벤트브릿지에 의해 1시간 마다 실행
- aws ECR로 환경설정
- 자세한 설명은 블로그 글 참고
   -  <a href= "https://velog.io/@hyeykim/원하는-웹사이트를-크롤링-해보자">원하는 웹사이트를 크롤링 해보자! </a>
   -  <a href= "https://velog.io/@hyeykim/lambda%EC%97%90-selenium-webdriver%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%9C-%ED%81%AC%EB%A1%A4%EB%A7%81-%EC%BD%94%EB%93%9C%EB%A5%BC-%EC%98%AC%EB%A0%A4%EB%B3%B4%EC%9E%90">lambda에 selenium, webdriver를 활용한 크롤링 코드를 올려보자! </a>
   -  <a href= "https://velog.io/@hyeykim/lambda%EC%97%90%EC%84%9C-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%9C-%EB%8D%B0%EC%9D%B4%ED%84%B0-s3%EC%97%90-%EC%97%85%EB%A1%9C%EB%93%9C-%ED%95%98%EA%B8%B0">lambda에서 크롤링한 데이터 s3에 업로드 하기 </a>
   - 각종 이슈 해결
      - <a href= "https://velog.io/@hyeykim/mac%EC%97%90%EC%84%9C-webdrivermanager%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%B4-chromedriver%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94-%EC%A4%91-OSError-Errno-8-Exec-format-error-%ED%95%B4%EA%B2%B0">mac에서 webdriver_manager를 사용해 chromedriver를 사용하는 중 OSError: [Errno 8] Exec format error: 해결 </a>
### lambda-s3-gemini-slack
- s3에 저장된 Json파일을 Genimi API로 보내 요약 정리된 후 Slack webHook API 호출하는 람다
- aws s3 Put이벤트 발생 시 실행
- aws ECR로 환경설정
