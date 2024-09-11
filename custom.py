import os, time, uuid
import pandas as pd
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry
from msrest.authentication import ApiKeyCredentials

# 환경 변수에서 Azure Custom Vision 서비스 정보 가져오기
VISION_TRAINING_ENDPOINT = os.environ["VISION_TRAINING_ENDPOINT"]
VISION_TRAINING_KEY = os.environ["VISION_TRAINING_KEY"]
VISION_PREDICTION_KEY = os.environ["VISION_PREDICTION_KEY"]
VISION_PREDICTION_RESOURCE_ID = os.environ["VISION_PREDICTION_RESOURCE_ID"]
prediction_endpoint = "https://healthkungyacv-prediction.cognitiveservices.azure.com/"

food_db = pd.read_excel("Food_DB.xlsx")

# Custom Vision 클라이언트 초기화
training_credentials = ApiKeyCredentials(in_headers={"Training-key": VISION_TRAINING_KEY})
trainer = CustomVisionTrainingClient(VISION_TRAINING_ENDPOINT, training_credentials)

prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": VISION_PREDICTION_KEY})
predictor = CustomVisionPredictionClient(prediction_endpoint, prediction_credentials)

# 프로젝트 ID와 퍼블리시 이름 설정
project_id = "56bddca9-b0ee-45b6-aa4b-064b5a618619"
publish_iteration_name = "Iteration3"

# 예측 처리
image_url = "https://t1.daumcdn.net/cfile/tistory/9986BC3C5DF1B5C31A"
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