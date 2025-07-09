import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

# 1. 엑셀 파일 경로
file_path = "업데이트 엑셀.xlsx"

# 엑셀 파일 존재 확인
if not os.path.exists(file_path):
    print(f"❌ 엑셀 파일을 찾을 수 없습니다: {file_path}")
    print("현재 디렉토리에 '업데이트 엑셀.xlsx' 파일을 넣어주세요.")
    exit()

# 2. 엑셀 열고 링크 모으기
try:
    xls = pd.ExcelFile(file_path)
    all_links = []

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        for col in df.columns:
            if df[col].astype(str).str.contains("http").any():
                links = df[col].dropna().astype(str).tolist()
                all_links.extend(links)

    print(f"총 {len(all_links)}개의 링크를 찾았습니다.")
    
    if len(all_links) == 0:
        print("❌ 엑셀 파일에서 링크를 찾을 수 없습니다.")
        exit()
        
except Exception as e:
    print(f"❌ 엑셀 파일 읽기 실패: {e}")
    exit()

# 3. Selenium으로 브라우저 열기
chromedriver_path = "chromedriver-mac-arm64/chromedriver"
if not os.path.exists(chromedriver_path):
    print(f"❌ chromedriver를 찾을 수 없습니다: {chromedriver_path}")
    exit()

try:
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)
    print("✅ 브라우저 실행 성공")
except Exception as e:
    print(f"❌ 브라우저 실행 실패: {e}")
    exit()

# 4. 링크 접속 테스트
for idx, link in enumerate(all_links):
    print(f"\n[{idx+1}] {link} 접속 중...")
    try:
        driver.get(link)
        time.sleep(3)  # 페이지 로딩 대기
        print("✅ 접속 성공")
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
    time.sleep(1)

driver.quit()
print("\n🧹 브라우저 종료 완료.")
