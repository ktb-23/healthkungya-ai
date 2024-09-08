# 에러메세지(ModuleNotFoundError: No module named 'bs4') 발생 시 가상 환경 내에서 패키지 설치
# 가상환경 실행 후 아래 코드를 터미널에 입력
# pip install bs4 requests selenium webdriver-manager

import os
import time  # 추가
import requests
from bs4 import BeautifulSoup
# webdriver-manager를 사용하여 ChromeDriver 설치 및 설정 (mac os, 5개 줄 추가함)
from selenium import webdriver  # 추가
from selenium.webdriver.chrome.service import Service  # 추가
from selenium.webdriver.common.by import By  # 추가
from webdriver_manager.chrome import ChromeDriverManager  # 추가


query = input("검색할 내용을 입력하세요 : ")
num_images = int(input("가져올 사진의 수를 입력하세요: "))
file_path = input("추가하고 싶은 파일 이름을 입력하세요 : ")

def download_images(query, num_images, file_path):
    # 브라우저 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Google 이미지 검색 페이지 열기
    search_url = f"https://www.google.com/search?q={query}&source=lnms&tbm=isch"
    driver.get(search_url)
    
    # 이미지가 충분히 로드되도록 스크롤 다운 반복
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 페이지 로딩 시간을 기다림
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height or len(driver.find_elements(By.TAG_NAME, 'img')) >= num_images:
            break
        last_height = new_height
    
    # 페이지 소스를 받아와서 BeautifulSoup으로 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    images = soup.find_all('img')
    
    # 이미지 저장 경로 설정
    full_path = os.path.expanduser('~'), 'Downloads', 'crawling', 'imgs', file_path  # 기본 다운로드 폴더 내
    # 경로가 없으면 생성
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    
    count = 0
    for img in images:
        if count >= num_images:
            break
        img_url = img.get('data-src') or img.get('src')
        
        # HTTP(S)로 시작하는 이미지 URL만 다운로드
        if img_url and img_url.startswith('http'):
            # 이미지 크기 필터링 (너비 및 높이가 일정 크기 이상일 때만 다운로드)
            try:
                width = int(img.get('width', 0))
                height = int(img.get('height', 0))
                
                # "logo" 또는 "icon" 등의 단어가 포함된 URL을 필터링
                if "logo" in img_url.lower() or "icon" in img_url.lower():
                    continue
                
                # 이미지 크기가 너무 작다면 건너뜀
                if width < 100 or height < 100:
                    continue
                
                # 이미지 다운로드
                response = requests.get(img_url)
                with open(os.path.join(full_path, f'{query}_{count}.jpg'), 'wb') as file:
                    file.write(response.content)
                count += 1
                
            except Exception as e:
                print(f"이미지 처리 중 오류 발생: {e}")

download_images(query, num_images, file_path)