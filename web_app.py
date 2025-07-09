import os
import time
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Choi Rocket: I don't give a shit !! 🖕</title>
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
        
        .upload-icon {
            font-size: 3em;
            margin-bottom: 15px;
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
        
        .chrome-status {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #2e7d32;
            font-weight: 600;
            text-align: center;
        }
        
        .chrome-error {
            background: #ffeaa7;
            border: 1px solid #fdcb6e;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #e17055;
            font-weight: 600;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🚀 Choi Rocket: I don't give a shit !! 🖕</h1>
            <p class="subtitle">엑셀 파일의 링크를 자동으로 클릭하여 버튼을 실행합니다</p>
        </div>
        
        <div class="chrome-status" id="chromeStatus">
            ✅ Chrome Remote Debugging 준비됨 (포트 9222)
        </div>
        
        <div class="upload-area">
            <div class="upload-icon">📊</div>
            <p><strong>엑셀 파일을 업로드하세요</strong></p>
            <p>링크가 포함된 .xlsx 또는 .xls 파일</p>
            <div class="file-input">
                <label for="file" class="file-label">파일 선택</label>
                <input type="file" id="file" accept=".xlsx,.xls">
            </div>
            <p id="fileName" style="margin-top: 15px; color: #667eea; font-weight: 600;"></p>
        </div>
        
        <div style="text-align: center;">
            <button class="btn" onclick="analyzeFile()" id="analyzeBtn" disabled>📊 링크 분석</button>
            <button class="btn" onclick="startAutomation()" id="startBtn" disabled>🚀 자동화 시작</button>
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
            startBtn.textContent = '🚀 자동화 시작';
            progressContainer.style.display = 'none';
        }
        
        // 초기 Chrome 상태 확인
        setTimeout(checkChromeStatus, 1000);
        
        function checkChromeStatus() {
            fetch('/chrome-status')
            .then(response => response.json())
            .then(data => {
                const chromeStatus = document.getElementById('chromeStatus');
                if (data.connected) {
                    chromeStatus.className = 'chrome-status';
                    chromeStatus.textContent = '✅ Chrome Remote Debugging 연결됨 (포트 9222)';
                } else {
                    chromeStatus.className = 'chrome-error';
                    chromeStatus.innerHTML = '⚠️ Chrome Remote Debugging 연결 실패<br/>터미널에서 다음 명령어를 실행하세요:<br/><code>open -a "Google Chrome" --args --remote-debugging-port=9222</code>';
                }
            })
            .catch(error => {
                console.error('Chrome 상태 확인 오류:', error);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chrome-status')
def chrome_status():
    """Chrome Remote Debugging 연결 상태 확인"""
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # 연결 테스트만 하고 바로 종료
        test_driver = webdriver.Chrome(options=options)
        test_driver.quit()
        
        return jsonify({'connected': True})
    except Exception as e:
        return jsonify({'connected': False, 'error': str(e)})

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
            
            link_count = len([cell for col in sheet_df.columns for cell in sheet_df[col] 
                            if pd.notna(cell) and isinstance(cell, str) and 'http' in str(cell).lower()])
            if link_count > 0:
                log_message(f"  📎 {col} 열에서 {link_count}개 링크 발견")
        
        if not found_links:
            return jsonify({'success': False, 'error': 'URL이 포함된 셀을 찾을 수 없습니다.'})
        
        log_message(f"✅ 총 {len(found_links)}개의 고유 링크를 찾았습니다!")
        for i, link in enumerate(found_links[:5], 1):  # 처음 5개만 로그에 표시
            log_message(f"  {i}. {link[:100]}{'...' if len(link) > 100 else ''}")
        
        if len(found_links) > 5:
            log_message(f"  ... 및 {len(found_links) - 5}개 더")
        
        return jsonify({
            'success': True,
            'total_links': len(found_links),
            'links': found_links
        })
        
    except Exception as e:
        error_msg = f"분석 중 오류 발생: {str(e)}"
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
        
        log_message("🚀 자동화 시작!")
        
        # Chrome 설정
        log_message("🔗 기존 브라우저에 연결 시도...")
        
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            driver = webdriver.Chrome(options=options)
            log_message("✅ 기존 브라우저 연결 성공!")
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

@app.route('/webhook/automation', methods=['POST'])
def webhook_automation():
    """Vercel에서 오는 자동화 요청 웹훅"""
    global found_links, process_status
    
    try:
        data = request.get_json()
        if not data or 'links' not in data:
            return jsonify({'success': False, 'error': '잘못된 데이터입니다.'})
        
        found_links = data['links']
        analysis_results = data.get('analysis_results', [])
        
        log_message(f"🔄 Vercel에서 {len(found_links)}개 링크 자동화 요청 받음")
        
        # 자동화 상태 초기화
        process_status = {
            'status': 'connecting',
            'progress': 0,
            'current_link': '',
            'total_links': len(found_links),
            'processed_links': 0,
            'logs': process_status.get('logs', []),
            'error': None
        }
        
        # 백그라운드에서 자동화 실행
        import threading
        automation_thread = threading.Thread(target=run_automation_background)
        automation_thread.daemon = True
        automation_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'{len(found_links)}개 링크 자동화 시작됨',
            'status_url': '/status'
        })
        
    except Exception as e:
        log_message(f"❌ 웹훅 처리 오류: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def run_automation_background():
    """백그라운드에서 자동화 실행"""
    global process_status
    
    try:
        log_message("🚀 백그라운드 자동화 시작!")
        
        # Chrome 설정
        log_message("🔗 기존 브라우저에 연결 시도...")
        
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            driver = webdriver.Chrome(options=options)
            log_message("✅ 기존 브라우저 연결 성공!")
        except Exception as e:
            error_msg = f"❌ 브라우저 연결 실패: {str(e)}"
            log_message(error_msg)
            process_status['status'] = 'error'
            process_status['error'] = error_msg
            return
        
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
        log_message("🎉 백그라운드 자동화 완료!")
        
    except Exception as e:
        error_msg = f"백그라운드 자동화 중 전체 오류: {str(e)}"
        log_message(f"❌ {error_msg}")
        process_status['status'] = 'error'
        process_status['error'] = error_msg

def try_auto_login(driver):
    """자동 로그인 시도"""
    try:
        # .env 파일에서 로그인 정보 읽기
        username = "paranormal"
        password = "wotjd214!@"
        
        # 로그인 폼 찾기
        username_field = None
        password_field = None
        
        # 다양한 선택자로 로그인 필드 찾기
        username_selectors = [
            "input[name='username']", "input[name='user_id']", "input[name='id']",
            "input[id='username']", "input[id='user_id']", "input[id='id']",
            "input[type='text']", "input[placeholder*='아이디']", "input[placeholder*='ID']"
        ]
        
        password_selectors = [
            "input[name='password']", "input[name='passwd']", "input[name='pw']",
            "input[id='password']", "input[id='passwd']", "input[id='pw']",
            "input[type='password']"
        ]
        
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if username_field and password_field:
            log_message("🔐 로그인 폼 발견, 자동 로그인 시도...")
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 찾기 및 클릭
            login_button_selectors = [
                "input[type='submit']", "button[type='submit']",
                "input[value*='로그인']", "button:contains('로그인')",
                ".login-btn", "#login_btn", ".btn-login"
            ]
            
            for selector in login_button_selectors:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    login_button.click()
                    log_message("✅ 로그인 버튼 클릭 완료")
                    time.sleep(3)  # 로그인 처리 대기
                    return
                except:
                    continue
            
            # 엔터키로 로그인 시도
            from selenium.webdriver.common.keys import Keys
            password_field.send_keys(Keys.RETURN)
            log_message("⌨️ 엔터키로 로그인 시도")
            time.sleep(3)
        
    except Exception as e:
        log_message(f"🔐 자동 로그인 중 오류 (계속 진행): {str(e)}")

def handle_alerts(driver):
    """알림 및 팝업 처리"""
    try:
        # JavaScript 알림 처리
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            log_message(f"🔔 알림 발견: {alert_text}")
            alert.accept()
            log_message("✅ 알림 확인 완료")
            time.sleep(1)
        except:
            pass
        
        # 자동화 감지 알림 처리
        automation_alert_selectors = [
            "div:contains('자동화된 접근')",
            "div:contains('로봇으로 판단')",
            ".alert", ".notice", ".warning",
            "[role='alert']", "[role='dialog']"
        ]
        
        for selector in automation_alert_selectors:
            try:
                alert_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in alert_elements:
                    if any(keyword in element.text for keyword in ['자동화', '로봇', '차단', 'automation', 'robot']):
                        log_message(f"🤖 자동화 감지 알림 발견: {element.text[:50]}...")
                        
                        # 확인 버튼 찾기
                        confirm_buttons = element.find_elements(By.CSS_SELECTOR, "button, input[type='button'], .btn")
                        for btn in confirm_buttons:
                            if any(keyword in btn.text.lower() for keyword in ['확인', '닫기', 'ok', 'close']):
                                btn.click()
                                log_message("✅ 자동화 알림 확인 완료")
                                time.sleep(1)
                                break
            except:
                continue
                
    except Exception as e:
        log_message(f"🔔 알림 처리 중 오류 (계속 진행): {str(e)}")

def click_target_button(driver):
    """목표 버튼 클릭"""
    try:
        # 여러 선택자로 버튼 찾기 시도
        button_selectors = [
            "#update_start",  # 기본 ID
            "button:contains('상품업데이트 & 마켓전송 시작')",
            "input[value*='상품업데이트']",
            "button[onclick*='update']",
            ".update-btn", ".start-btn"
        ]
        
        button_found = False
        
        for selector in button_selectors:
            try:
                if ":contains" in selector:
                    # XPath로 텍스트 검색
                    xpath = f"//button[contains(text(), '상품업데이트 & 마켓전송 시작')] | //input[contains(@value, '상품업데이트')]"
                    button = driver.find_element(By.XPATH, xpath)
                else:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                
                # 버튼이 클릭 가능한지 확인
                if button.is_enabled() and button.is_displayed():
                    button.click()
                    log_message("🎯 목표 버튼 클릭 성공!")
                    button_found = True
                    time.sleep(2)
                    break
                    
            except Exception as e:
                continue
        
        if not button_found:
            log_message("⚠️ 목표 버튼을 찾을 수 없음 (페이지는 정상 로드됨)")
            
    except Exception as e:
        log_message(f"🎯 버튼 클릭 중 오류: {str(e)}")

@app.route('/status')
def get_status():
    return jsonify(process_status)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌐 웹 서버 시작됨!")
    print("👉 브라우저에서 http://localhost:8080 으로 접속하세요!")
    print("="*50 + "\n")
    
    log_message("🌐 웹 서버 시작됨!")
    log_message("👉 브라우저에서 http://localhost:8080 으로 접속하세요!")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 