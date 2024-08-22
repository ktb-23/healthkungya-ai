# custom_app.py에서 실행 안될 시 재설정방법
# 가상환경 설정 python -m venv venv
# activate
# pip install azure-cognitiveservices-vision-customvision
# pip install pandas
# pip install msrest
# pip install flask
# pip install openpyxl

import os
import pandas as pd
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry
from msrest.authentication import ApiKeyCredentials

# 환경 변수에서 Azure Custom Vision 서비스 정보 가져오기
training_endpoint = "https://aidencustom01.cognitiveservices.azure.com/"
training_key = "3ff38530af324ce2bcb22c2014aabe32"
prediction_key = "ac629f102a6a4ccb98166f95915c68ff"
prediction_resource_id = "/subscriptions/49719505-a401-4b7a-a1ab-bef190ae283f/resourceGroups/aiden-test/providers/Microsoft.CognitiveServices/accounts/aidencustom01-Prediction"
prediction_endpoint = "https://aidencustom01-prediction.cognitiveservices.azure.com/"

food_db = pd.read_excel("Food_DB.xlsx")

# Custom Vision 클라이언트 초기화
training_credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(training_endpoint, training_credentials)

prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(prediction_endpoint, prediction_credentials)

# 프로젝트 ID와 퍼블리시 이름 설정
project_id = "19edf899-ae63-4c2f-b404-588902ecc8a0"
publish_iteration_name = "Iteration1"

# 예측 처리
image_url = "https://recipe1.ezmember.co.kr/cache/recipe/2015/08/27/932b0eac49b0f341ee9b91553d84d9b91.jpg"
results = predictor.classify_image_url(project_id, publish_iteration_name, image_url)

# 예측된 태그 처리
if results.predictions:
    detected_tags = [prediction.tag_name for prediction in results.predictions]
    print("Detected tags:", detected_tags)
    
    found = False
    for tag in detected_tags:
        tag = tag.strip()
        print(f"Checking if '{tag}' is in the database...")
        
        # 음식 이름 칼럼에서 공백 제거
        food_db['음 식 명'] = food_db['음 식 명'].str.strip()
        
        # 데이터베이스에서 일치하는 음식 이름 찾기
        if tag in food_db['음 식 명'].values:
            matching_row = food_db[food_db['음 식 명'] == tag]
            r_value = matching_row['에너지(kcal)'].values[0]
            print(f"'{tag}' kcal: {r_value}")
            found = True
            break  # 첫 번째 일치하는 결과를 찾으면 루프 종료
    
    if not found:
        print("No matching tags found in the database.")
else:
    print("No tags detected.")