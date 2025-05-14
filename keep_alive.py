import requests
import time

# 주기적으로 요청을 보낼 URL 설정
url = 'https://janghungo-bunsilmul-gwanri.onrender.com'

while True:
    try:
        # URL에 GET 요청 보내기
        response = requests.get(url)
        
        # 상태 코드 출력 (200이면 정상 응답)
        print(f"Status Code: {response.status_code} - Website is active")
    except requests.exceptions.RequestException as e:
        # 오류가 발생하면 출력
        print(f"Error: {e}")
    
    # 5분 (300초)마다 요청 보내기
    time.sleep(300)
