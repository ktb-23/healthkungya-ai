# 가상환경 생성: python -m venv venv
# 가상환경 실행: activate (또는 source venv/bin/activate)
# 필요한 모듈 설치: pip install -r requirements.txt
# 서버 실행: flask --app custom_app run --port 5001
# 가상환경 종료: deactivate

from flask import Flask, request, jsonify
import pandas as pd
from azure.cognitiveservices.vision.customvision.prediction import (
    CustomVisionPredictionClient,
)
from msrest.authentication import ApiKeyCredentials
import requests
import threading

app = Flask(__name__)
app.secret_key = "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ"  # 세션을 사용하기 위해 필요

# Custom Vision 설정
prediction_endpoint = "https://healthkungyacv-prediction.cognitiveservices.azure.com/"
# XXX: 키가 코드에 직접 들어가 있습니다. 환경변수로 옮기는 것이 좋습니다.
prediction_key = "7c0683360f1e4e6f937f3c3fa111f233"

# DB 파일 읽어오기
food_db = pd.read_excel("Food_DB.xlsx")
food_db["음 식 명"] = food_db["음 식 명"].str.strip()

# Custom Vision Prediction 클라이언트 초기화
prediction_credentials = ApiKeyCredentials(
    in_headers={"Prediction-key": prediction_key}
)
predictor = CustomVisionPredictionClient(prediction_endpoint, prediction_credentials)

# 프로젝트 ID와 퍼블리시 설정
project_id = "56bddca9-b0ee-45b6-aa4b-064b5a618619"
publish_iteration_name = "Iteration3"


def get_kcal_of_tag_in_db(tag):
    tag = tag.strip()

    matching_row = food_db[food_db["음 식 명"] == tag]

    if matching_row.empty:
        return None

    else:
        return matching_row["에너지(kcal)"].values[0]


def predict_image(image_url, foodlog_id):
    print("Predicting image...")
    results = predictor.classify_image_url(
        project_id, publish_iteration_name, image_url
    )

    detected_tags = []

    if results.predictions:
        detected_tags = [prediction.tag_name for prediction in results.predictions]

    if not detected_tags:
        return jsonify({"error": "예측된 태그가 없습니다."}), 404

    results = []
    for tag in detected_tags:
        kcal = get_kcal_of_tag_in_db(tag)
        if kcal is not None:
            results.append({"kcal": kcal, "tag": tag, "foodlog_id": foodlog_id})

    main_server_domain = "http://172.30.3.159:8000/"  # NOTE: 상황에 맞게 수정
    url = main_server_domain + "/api/food/result"  # NOTE: 상황에 맞게 수정

    # NOTE: 메인 서버로 결과 전송
    requests.post(
        url,
        json=(
            results[0]
            if results
            else {"kal": None, "tag": None, "foodlog_id": foodlog_id}
        ),
    )


@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Custom Vision Prediction API!", 200


@app.route("/predict", methods=["GET"])
def get_image_url():

    # NOTE: ai에게 보낼 image_url과 처리 완료 후 이미지 식별용 foodlog_id
    image_url = request.args.get("image_url")
    foodlog_id = request.args.get("foodlog_id")

    if not image_url or not foodlog_id:
        return jsonify({"error": "잘못된 형식의 요청입니다."}), 400

    threading.Thread(target=predict_image, args=(image_url, foodlog_id)).start()

    return (jsonify({"message": "이미지 분석 요청이 정상적으로 처리되었습니다."}), 200)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
