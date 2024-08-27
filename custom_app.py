# 가상환경 설정 python -m venv venv
# 가상환경 실행 activate
# python custom_app.py 입력
# 가상환경 종료 deactivate

from flask import Flask, request, jsonify, session
import pandas as pd
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

import os
from flask import Flask, request, jsonify, session, send_from_directory
import pandas as pd
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from dotenv import load_dotenv
import os
load_dotenv()  # .env 파일에서 환경 변수를 불러옴
training_key = os.getenv('VISION_TRAINING_KEY')
training_endpoint = os.getenv('VISION_TRAINING_ENDPOINT')


app = Flask(__name__)
app.secret_key = 'a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ' # 세션을 사용하기 위해 필요

# Custom Vision 설정
prediction_endpoint = "https://healthkungyacv-prediction.cognitiveservices.azure.com/"
prediction_key = "7c0683360f1e4e6f937f3c3fa111f233"

# DB 파일 읽어오기
food_db = pd.read_excel("Food_DB.xlsx")

# Custom Vision Prediction 클라이언트 초기화
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(prediction_endpoint, prediction_credentials)

# 프로젝트 ID와 퍼블리시 설정
project_id = "56bddca9-b0ee-45b6-aa4b-064b5a618619"
publish_iteration_name = "Iteration3"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Custom Vision Prediction API!", 200

@app.route('/predict', methods=['GET'])
def get_image_url():
    # 이미지 URL을 GET 요청 / 풀스택분들이 전달해주는 image_url
    image_url = request.args.get('image_url')

    if not image_url:
        return jsonify({"error": "이미지 URL이 제공되지 않았습니다."}), 400

    results = predictor.classify_image_url(project_id, publish_iteration_name, image_url)

    if results.predictions:
        detected_tags = [prediction.tag_name for prediction in results.predictions]
        session['detected_tags'] = detected_tags  # 예측 결과를 세션에 저장
        return jsonify({"message": "이미지 URL이 성공적으로 처리되었습니다.", "tags": detected_tags}), 200
    else:
        return jsonify({"message": "태그가 감지되지 않았습니다."}), 404

@app.route('/result', methods=['POST'])
def post_prediction_result():
    detected_tags = session.get('detected_tags')

    if not detected_tags:
        return jsonify({"error": "예측된 태그가 없습니다."}), 400

    found = False
    response_data = {}

    for tag in detected_tags:
        tag = tag.strip()
        print(f"'{tag}'이 데이터베이스에 있는지 확인 중...")

        food_db['음 식 명'] = food_db['음 식 명'].str.strip()

        if tag in food_db['음 식 명'].values:
            matching_row = food_db[food_db['음 식 명'] == tag]
            r_value = matching_row['에너지(kcal)'].values[0]
            response_data = {
                "tag": tag,
                "kcal": r_value
            }
            found = True
            break

    if found:
        return jsonify(response_data)
    else:
        return jsonify({"message": "데이터베이스에서 일치하는 태그를 찾을 수 없습니다."}), 404

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
    # mac os에서 airplay receiver이 5000번 포트를 사용중이라 5001로 변경