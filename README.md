## 크롤링 전체 아키텍쳐
![크롤링 전체 아키텍쳐](https://cdn.discordapp.com/attachments/793022818757509131/1276880093188325388/2024-08-23_9.47.02.png?ex=66cb22c1&is=66c9d141&hm=d04c2ac33b726ac27998d64f9819e59a95ac2adec4a97b197a047278d5f18ba6&)

### lambda-selenium-docker: 
- 웹 사이트에서 글을 크롤링한 후 s3에 저장하는 람다
- aws 이벤트브릿지에 의해 1시간 마다 실행
- aws ECR로 환경설정
   
### lambda-s3-gemini-slack
- s3에 저장된 Json파일을 Genimi API로 보내 요약 정리된 후 Slack webHook API 호출하는 람다
- aws s3 Put이벤트 발생 시 실행
- aws ECR로 환경설정
