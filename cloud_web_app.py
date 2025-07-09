#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.common.exceptions import (
    WebDriverException, 
    TimeoutException, 
    NoSuchElementException,
    UnexpectedAlertPresentException
)

# 상세 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 전역 변수
found_links = []
process_status = {
    'status': 'ready',
    'progress': 0,
    'current_link': '',
    'total_links': 0,
    'processed_links': 0,
    'logs': [],
    'error': None
}

def log_message(message):
    """로그 메시지를 기록하고 화면에 표시"""
    logger.info(message)
    process_status['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    if len(process_status['logs']) > 100:  # 최대 100개의 로그 유지
        process_status['logs'] = process_status['logs'][-100:]

def get_cloud_chrome_driver():
    """클라우드 환경용 Chrome 드라이버 생성"""
    options = Options()
    
    # Codespaces/클라우드 환경용 설정
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    try:
        driver = webdriver.Chrome(options=options)
        log_message("✅ 클라우드 Chrome 브라우저 연결 성공!")
        return driver
    except Exception as e:
        raise Exception(f"Chrome 드라이버 생성 실패: {str(e)}")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Excel Link Auto Clicker - Cloud Edition</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 800px;
            width: 90%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .title {
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.1em;
            color: #666;
            font-weight: 300;
        }
        
        .cloud-badge {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin: 10px 0;
            display: inline-block;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            transition: all 0.3s ease;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: rgba(118, 75, 162, 0.1);
        }
        
        .file-input {
            margin: 20px 0;
        }
        
        .file-input input[type="file"] {
            display: none;
        }
        
        .file-label {
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .file-label:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress-container {
            margin: 30px 0;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            display: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 12px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 6px;
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .status {
            text-align: center;
            font-weight: 600;
            margin: 10px 0;
            color: #667eea;
        }
        
        .log-container {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            border: 1px solid #e9ecef;
        }
        
        .log-item {
            margin: 5px 0;
            color: #495057;
        }
        
        .analysis-result {
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            display: none;
        }
        
        .link-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .error-message {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 15px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 600;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🚀 Excel Link Auto Clicker</h1>
            <div class="cloud-badge">☁️ Cloud Edition - Ready to Run!</div>
            <p class="subtitle">GitHub Codespaces에서 완전 자동화 실행</p>
        </div>
        
        <div class="upload-area">
            <div style="font-size: 3em; margin-bottom: 15px;">📊</div>
            <p><strong>Excel 파일을 업로드하세요</strong></p>
            <p>링크가 포함된 .xlsx 또는 .xls 파일</p>
            <div class="file-input">
                <label for="file" class="file-label">파일 선택</label>
                <input type="file" id="file" accept=".xlsx,.xls">
            </div>
            <p id="fileName" style="margin-top: 15px; color: #667eea; font-weight: 600;"></p>
        </div>
        
        <div style="text-align: center;">
            <button class="btn" onclick="analyzeFile()" id="analyzeBtn" disabled>📊 링크 분석</button>
            <button class="btn" onclick="startAutomation()" id="startBtn" disabled>🚀 완전 자동화 시작</button>
        </div>
        
        <div class="error-message" id="errorMessage"></div>
        
        <div class="analysis-result" id="analysisResult">
            <h3>📋 분석 결과</h3>
            <div id="linksList"></div>
        </div>
        
        <div class="progress-container" id="progressContainer">
            <div class="status" id="statusText">준비 중...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="progressText">0/0 완료</div>
        </div>
        
        <div class="log-container" id="logContainer" style="display: none;">
            <h3>📝 실행 로그</h3>
            <div id="logs"></div>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('file');
        const fileName = document.getElementById('fileName');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const startBtn = document.getElementById('startBtn');
        const errorMessage = document.getElementById('errorMessage');
        const analysisResult = document.getElementById('analysisResult');
        const progressContainer = document.getElementById('progressContainer');
        const logContainer = document.getElementById('logContainer');
        
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                fileName.textContent = `선택된 파일: ${e.target.files[0].name}`;
                analyzeBtn.disabled = false;
            }
        });
        
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
        
        function analyzeFile() {
            const file = fileInput.files[0];
            if (!file) {
                showError('파일을 선택해주세요.');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = '분석 중...';
            
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAnalysisResult(data);
                    startBtn.disabled = false;
                } else {
                    showError(data.error || '분석 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                showError('분석 중 오류가 발생했습니다: ' + error);
            })
            .finally(() => {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = '📊 링크 분석';
            });
        }
        
        function showAnalysisResult(data) {
            const linksList = document.getElementById('linksList');
            linksList.innerHTML = `
                <p><strong>총 ${data.total_links}개의 고유 링크를 찾았습니다!</strong></p>
                ${data.links.map((link, index) => `
                    <div class="link-item">
                        <strong>${index + 1}.</strong> ${link.length > 100 ? link.substring(0, 100) + '...' : link}
                    </div>
                `).join('')}
            `;
            analysisResult.style.display = 'block';
        }
        
        function startAutomation() {
            startBtn.disabled = true;
            startBtn.textContent = '실행 중...';
            progressContainer.style.display = 'block';
            logContainer.style.display = 'block';
            
            fetch('/start', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    pollStatus();
                } else {
                    showError(data.error || '자동화 시작 중 오류가 발생했습니다.');
                    resetUI();
                }
            })
            .catch(error => {
                showError('자동화 시작 중 오류가 발생했습니다: ' + error);
                resetUI();
            });
        }
        
        function pollStatus() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                updateProgress(data);
                
                if (data.status === 'running' || data.status === 'connecting') {
                    setTimeout(pollStatus, 1000);
                } else if (data.status === 'completed') {
                    resetUI();
                    alert('🎉 모든 링크 처리가 완료되었습니다!');
                } else if (data.status === 'error') {
                    resetUI();
                    showError(data.error || '처리 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                console.error('상태 확인 오류:', error);
                setTimeout(pollStatus, 2000);
            });
        }
        
        function updateProgress(data) {
            const statusText = document.getElementById('statusText');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const logs = document.getElementById('logs');
            
            statusText.textContent = data.current_link || '처리 중...';
            
            if (data.total_links > 0) {
                const percent = (data.processed_links / data.total_links) * 100;
                progressFill.style.width = percent + '%';
                progressText.textContent = `${data.processed_links}/${data.total_links} 완료`;
            }
            
            if (data.logs && data.logs.length > 0) {
                logs.innerHTML = data.logs.map(log => `<div class="log-item">${log}</div>`).join('');
                logs.scrollTop = logs.scrollHeight;
            }
        }
        
        function resetUI() {
            startBtn.disabled = false;
            startBtn.textContent = '🚀 완전 자동화 시작';
            progressContainer.style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_file():
    global found_links
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다.'})
        
        log_message("📊 링크 분석 시작...")
        
        # 엑셀 파일 읽기
        try:
            df = pd.read_excel(file, sheet_name=None)  # 모든 시트 읽기
        except Exception as e:
            return jsonify({'success': False, 'error': f'엑셀 파일 읽기 오류: {str(e)}'})
        
        found_links = []
        
        # 각 시트 분석
        for sheet_name, sheet_df in df.items():
            log_message(f"📄 {sheet_name} 시트 분석 중...")
            
            for col in sheet_df.columns:
                for idx, cell in enumerate(sheet_df[col]):
                    if pd.notna(cell) and isinstance(cell, str):
                        if 'http' in cell.lower():
                            # URL이 포함된 경우
                            links_in_cell = [link.strip() for link in cell.split() if 'http' in link.lower()]
                            for link in links_in_cell:
                                if link not in found_links:
                                    found_links.append(link)
        
        if not found_links:
            return jsonify({'success': False, 'error': 'URL이 포함된 셀을 찾을 수 없습니다.'})
        
        log_message(f"🔗 총 {len(found_links)}개의 고유 링크 발견!")
        
        return jsonify({
            'success': True,
            'total_links': len(found_links),
            'links': found_links
        })
        
    except Exception as e:
        error_msg = f"분석 오류: {str(e)}"
        log_message(f"❌ {error_msg}")
        return jsonify({'success': False, 'error': error_msg})

@app.route('/start', methods=['POST'])
def start_automation():
    global process_status
    
    try:
        if not found_links:
            return jsonify({'success': False, 'error': '먼저 파일을 분석해주세요.'})
        
        # 상태 초기화
        process_status = {
            'status': 'connecting',
            'progress': 0,
            'current_link': '',
            'total_links': len(found_links),
            'processed_links': 0,
            'logs': process_status['logs'],  # 기존 로그 유지
            'error': None
        }
        
        log_message("🚀 클라우드 자동화 시작!")
        
        # 클라우드 Chrome 드라이버 생성
        try:
            driver = get_cloud_chrome_driver()
        except Exception as e:
            error_msg = f"❌ 브라우저 연결 실패: {str(e)}"
            log_message(error_msg)
            process_status['status'] = 'error'
            process_status['error'] = error_msg
            return jsonify({'success': False, 'error': error_msg})
        
        process_status['status'] = 'running'
        
        # 각 링크 처리
        for i, link in enumerate(found_links):
            try:
                process_status['current_link'] = f"링크 {i+1}/{len(found_links)} 처리 중..."
                process_status['progress'] = (i / len(found_links)) * 100
                
                log_message(f"🌐 링크 {i+1} 접속: {link[:80]}{'...' if len(link) > 80 else ''}")
                
                driver.get(link)
                time.sleep(3)  # 페이지 로드 대기
                
                # 자동 로그인 시도
                try_auto_login(driver)
                
                # 알림 처리
                handle_alerts(driver)
                
                # 버튼 클릭 시도
                click_target_button(driver)
                
                process_status['processed_links'] = i + 1
                log_message(f"✅ 링크 {i+1} 처리 완료")
                
                time.sleep(2)  # 다음 링크로 이동 전 대기
                
            except Exception as e:
                error_msg = f"링크 {i+1} 처리 중 오류: {str(e)}"
                log_message(f"⚠️ {error_msg}")
                continue  # 다음 링크 계속 처리
        
        driver.quit()
        process_status['status'] = 'completed'
        log_message("🎉 모든 링크 처리 완료!")
        
        return jsonify({'success': True})
        
    except Exception as e:
        error_msg = f"자동화 중 전체 오류: {str(e)}"
        log_message(f"❌ {error_msg}")
        process_status['status'] = 'error'
        process_status['error'] = error_msg
        return jsonify({'success': False, 'error': error_msg})

def try_auto_login(driver):
    """자동 로그인 시도"""
    try:
        username = "paranormal"
        password = "wotjd214!@"
        
        # 로그인 필드 찾기
        username_selectors = [
            "input[name='username']", "input[name='user_id']", "input[name='id']",
            "input[id='username']", "input[id='user_id']", "input[id='id']"
        ]
        
        password_selectors = [
            "input[name='password']", "input[name='passwd']", "input[name='pw']",
            "input[id='password']", "input[id='passwd']", "input[id='pw']"
        ]
        
        username_field = None
        password_field = None
        
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if username_field and password_field:
            log_message("🔐 로그인 폼 발견, 자동 로그인 시도...")
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 찾기 및 클릭
            login_selectors = [
                "input[type='submit']", "button[type='submit']", 
                "input[value*='로그인']", "button[text*='로그인']"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    login_btn.click()
                    log_message("✅ 자동 로그인 완료!")
                    time.sleep(2)
                    return
                except NoSuchElementException:
                    continue
            
            log_message("⚠️ 로그인 버튼을 찾을 수 없음")
    except Exception as e:
        log_message(f"⚠️ 자동 로그인 중 오류: {str(e)}")

def handle_alerts(driver):
    """팝업 및 알림 처리"""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        log_message(f"🚨 알림 감지: {alert_text}")
        alert.accept()
        log_message("✅ 알림 처리 완료")
    except:
        pass  # 알림이 없으면 무시

def click_target_button(driver):
    """타겟 버튼 클릭"""
    try:
        button_selectors = [
            "#update_start",
            "input[value*='상품업데이트']",
            "button[text*='상품업데이트']",
            "input[value*='시작']",
            "button[text*='시작']",
            "input[type='button'][value*='업데이트']",
            "button[class*='update']",
            "a[href*='update']"
        ]
        
        for selector in button_selectors:
            try:
                button = driver.find_element(By.CSS_SELECTOR, selector)
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    log_message(f"🎯 버튼 클릭 성공: {selector}")
                    time.sleep(1)
                    return
            except NoSuchElementException:
                continue
        
        log_message("⚠️ 타겟 버튼을 찾을 수 없음")
    except Exception as e:
        log_message(f"⚠️ 버튼 클릭 중 오류: {str(e)}")

@app.route('/status')
def get_status():
    return jsonify(process_status)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌟 GitHub Codespaces용 Excel Link Auto Clicker 실행됨!")
    print("🔗 포트 8080이 자동으로 공개됩니다!")
    print("📱 VS Code에서 'Ports' 탭을 확인하여 웹 링크를 클릭하세요!")
    print("="*70 + "\n")
    
    log_message("🌟 클라우드 웹 서버 시작됨!")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 