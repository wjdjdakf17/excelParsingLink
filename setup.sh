#!/bin/bash

echo "🚀 Excel Link Auto Clicker 환경 설정 시작..."

# Chrome 설치 및 설정
echo "📦 Google Chrome 설치 중..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# ChromeDriver 다운로드
echo "🔧 ChromeDriver 설정 중..."
CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 가상 디스플레이 설정
echo "🖥️ 가상 디스플레이 설정 중..."
sudo apt-get install -y xvfb

# Python 패키지 설치 확인
echo "🐍 Python 패키지 확인 중..."
pip install -r requirements.txt

echo "✅ 설정 완료! 이제 python3 web_app.py 로 실행하세요!"
echo "📱 GitHub Codespaces 포트 8080이 자동으로 외부에 공개됩니다!" 