import requests

# 세션 생성
session = requests.Session()

# 1. /predict 엔드포인트로 GET 요청 보내기
predict_url = "http://127.0.0.1:5001/predict"
image_url = "https://recipe1.ezmember.co.kr/cache/recipe/2022/09/04/37a1f64e7f0b5d2b5f89e92c4ef33a371.jpg"
params = {'image_url': image_url}

response = session.get(predict_url, params=params)

# 예측 결과 확인
if response.status_code == 200:
    print("Predict Response:", response.json())
else:
    print(f"Predict request failed with status code: {response.status_code}")

# 2. /result 엔드포인트로 POST 요청 보내기
result_url = "http://127.0.0.1:5001/result"
headers = {"Content-Type": "application/json"}
data = {}

response = session.post(result_url, headers=headers, json=data)

# 결과 확인
if response.status_code == 200:
    print("Result Response:", response.json())
else:
    print(f"Result request failed with status code: {response.status_code}")