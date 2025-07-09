from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 전역 변수
driver = None
current_task = {
    'is_running': False,
    'progress': 0,
    'total': 0,
    'logs': [],
    'links': []
}

def log_message(message):
    """로그 메시지 추가"""
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    current_task['logs'].append(log_entry)
    print(log_entry)  # 콘솔에도 출력

def analyze_excel(file_path):
    """엑셀 파일에서 링크 추출"""
    try:
        log_message("📊 링크 분석 시작...")
        
        # 엑셀 파일 읽기
        xls = pd.ExcelFile(file_path)
        links = []
        
        for sheet_name in xls.sheet_names:
            log_message(f"📄 {sheet_name} 시트 분석 중...")
            df = xls.parse(sheet_name)
            
            for col in df.columns:
                if df[col].astype(str).str.contains("http", na=False).any():
                    sheet_links = df[col].dropna().astype(str).tolist()
                    # http로 시작하는 링크만 필터링
                    valid_links = [link for link in sheet_links if link.startswith('http')]
                    links.extend(valid_links)
                    log_message(f"  📎 {col} 열에서 {len(valid_links)}개 링크 발견")
        
        # 중복 제거
        unique_links = list(set(links))
        
        if unique_links:
            log_message(f"✅ 총 {len(unique_links)}개의 고유 링크를 찾았습니다!")
            for i, link in enumerate(unique_links[:3]):  # 처음 3개만 표시
                log_message(f"  {i+1}. {link}")
            if len(unique_links) > 3:
                log_message(f"  ... 및 {len(unique_links) - 3}개 더")
        else:
            log_message("❌ 링크를 찾을 수 없습니다.")
            
        return unique_links
        
    except Exception as e:
        error_msg = f"❌ 분석 실패: {str(e)}"
        log_message(error_msg)
        return []

def run_automation(links, button_selector, delay):
    """자동화 실행"""
    global driver, current_task
    
    current_task['is_running'] = True
    current_task['progress'] = 0
    current_task['total'] = len(links)
    
    try:
        log_message("🚀 자동화 시작!")
        
        # 브라우저 실행
        chromedriver_path = "chromedriver-mac-arm64/chromedriver"
        if not os.path.exists(chromedriver_path):
            raise Exception(f"chromedriver를 찾을 수 없습니다: {chromedriver_path}")
            
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service)
        log_message("✅ 브라우저 실행됨")
        
        for i, link in enumerate(links):
            if not current_task['is_running']:
                break
                
            log_message(f"🔗 [{i+1}/{len(links)}] {link} 접속 중...")
            
            try:
                # 페이지 접속
                driver.get(link)
                time.sleep(delay)
                
                # 버튼 찾기 및 클릭
                try:
                    if button_selector.startswith('#'):
                        # ID로 찾기
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.ID, button_selector[1:]))
                        )
                    elif button_selector.startswith('.'):
                        # 클래스로 찾기
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, button_selector[1:]))
                        )
                    elif button_selector.startswith('text:'):
                        # 텍스트로 찾기
                        text_to_find = button_selector[5:]  # 'text:' 제거
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text_to_find}')]"))
                        )
                    else:
                        # 태그명으로 찾기
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.TAG_NAME, button_selector))
                        )
                    
                    button.click()
                    log_message(f"  ✅ 버튼 클릭 성공!")
                    
                except Exception as e:
                    log_message(f"  ⚠️ 버튼 클릭 실패: {str(e)}")
                    
                time.sleep(1)  # 추가 대기
                
            except Exception as e:
                log_message(f"  ❌ 접속 실패: {str(e)}")
            
            # 진행률 업데이트
            current_task['progress'] = i + 1
            
    except Exception as e:
        error_msg = f"❌ 자동화 실행 실패: {str(e)}"
        log_message(error_msg)
        
    finally:
        stop_automation()

def stop_automation():
    """자동화 중지"""
    global driver, current_task
    
    current_task['is_running'] = False
    
    if driver:
        try:
            driver.quit()
            log_message("🧹 브라우저 종료됨")
        except:
            pass
        finally:
            driver = None
            
    log_message("⏹️ 자동화 중지됨")

@app.route('/')
def index():
    """메인 페이지"""
    return '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 링크 자동 클릭 프로그램</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
        }
        
        .title {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .section {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }
        
        .section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        
        input[type="file"], input[type="text"], input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 25px;
            margin: 5px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-danger { background: #dc3545; color: white; }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress-container {
            margin: 20px 0;
        }
        
        .progress-bar {
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s;
            position: relative;
        }
        
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            color: #333;
            z-index: 10;
        }
        
        .log-container {
            height: 300px;
            overflow-y: auto;
            background: #000;
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .status {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .status.ready { background: #d4edda; color: #155724; }
        .status.running { background: #fff3cd; color: #856404; }
        .status.stopped { background: #f8d7da; color: #721c24; }
        
        .helper-text {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .emoji {
            font-size: 1.2em;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🚀 링크 자동 클릭 프로그램</h1>
        
        <div class="section">
            <h3><span class="emoji">📁</span>엑셀 파일 선택</h3>
            <div class="form-group">
                <input type="file" id="excelFile" accept=".xlsx,.xls">
                <div class="helper-text">📋 링크가 포함된 엑셀 파일을 선택하세요</div>
            </div>
            <button class="btn btn-primary" onclick="analyzeFile()">
                <span class="emoji">📊</span>링크 분석
            </button>
            <span id="analyzeStatus" class="status ready">준비</span>
        </div>
        
        <div class="section">
            <h3><span class="emoji">🎯</span>자동화 설정</h3>
            <div class="form-group">
                <label for="buttonSelector">클릭할 버튼:</label>
                <input type="text" id="buttonSelector" value="button" placeholder="예: button, .btn, #submit">
                <div class="helper-text">💡 button(태그), .btn(클래스), #submit(ID) 형식으로 입력</div>
            </div>
            <div class="form-group">
                <label for="delay">페이지 로딩 대기 시간 (초):</label>
                <input type="number" id="delay" value="3" min="1" max="10">
            </div>
        </div>
        
        <div class="section">
            <h3><span class="emoji">🎮</span>제어판</h3>
            <button class="btn btn-warning" onclick="startAutomation()">
                <span class="emoji">🚀</span>자동화 시작
            </button>
            <button class="btn btn-danger" onclick="stopAutomation()">
                <span class="emoji">⏹️</span>중지
            </button>
            <span id="runStatus" class="status ready">대기 중</span>
            
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                    <div class="progress-text" id="progressText">0%</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3><span class="emoji">📋</span>실행 로그</h3>
            <div class="log-container" id="logContainer">
                [시작] 링크 자동 클릭 프로그램이 준비되었습니다! 🚀
            </div>
        </div>
    </div>

    <script>
        let updateInterval;
        
        function analyzeFile() {
            const fileInput = document.getElementById('excelFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('엑셀 파일을 먼저 선택해주세요!');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            updateStatus('analyzeStatus', 'running', '분석 중...');
            
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus('analyzeStatus', 'ready', `${data.count}개 링크 발견`);
                } else {
                    updateStatus('analyzeStatus', 'stopped', '분석 실패');
                    alert('분석 실패: ' + data.error);
                }
                updateLogs();
            })
            .catch(error => {
                updateStatus('analyzeStatus', 'stopped', '오류 발생');
                console.error('Error:', error);
            });
        }
        
        function startAutomation() {
            const buttonSelector = document.getElementById('buttonSelector').value.trim();
            const delay = parseInt(document.getElementById('delay').value);
            
            if (!buttonSelector) {
                alert('클릭할 버튼을 입력해주세요!');
                return;
            }
            
            fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    button_selector: buttonSelector,
                    delay: delay
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus('runStatus', 'running', '실행 중');
                    startUpdating();
                } else {
                    alert('시작 실패: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        
        function stopAutomation() {
            fetch('/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                updateStatus('runStatus', 'stopped', '중지됨');
                stopUpdating();
            });
        }
        
        function updateStatus(elementId, status, text) {
            const element = document.getElementById(elementId);
            element.className = `status ${status}`;
            element.textContent = text;
        }
        
        function updateLogs() {
            fetch('/status')
            .then(response => response.json())
            .then(data => {
                const logContainer = document.getElementById('logContainer');
                logContainer.innerHTML = data.logs.join('\\n');
                logContainer.scrollTop = logContainer.scrollHeight;
                
                // 진행률 업데이트
                if (data.total > 0) {
                    const progress = (data.progress / data.total) * 100;
                    document.getElementById('progressFill').style.width = progress + '%';
                    document.getElementById('progressText').textContent = 
                        `${data.progress}/${data.total} (${Math.round(progress)}%)`;
                }
                
                if (!data.is_running && data.progress > 0) {
                    updateStatus('runStatus', 'ready', '완료');
                    stopUpdating();
                }
            });
        }
        
        function startUpdating() {
            updateInterval = setInterval(updateLogs, 1000);
        }
        
        function stopUpdating() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        }
        
        // 초기 로그 업데이트
        updateLogs();
    </script>
</body>
</html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    """엑셀 파일 분석"""
    global current_task
    
    try:
        # 로그 초기화
        current_task['logs'] = []
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다.'})
        
        # 파일 저장
        filename = secure_filename(file.filename)
        file_path = os.path.join('.', filename)
        file.save(file_path)
        
        # 링크 분석
        links = analyze_excel(file_path)
        current_task['links'] = links
        
        # 임시 파일 삭제
        os.remove(file_path)
        
        return jsonify({
            'success': True, 
            'count': len(links),
            'links': links[:5]  # 처음 5개만 반환
        })
        
    except Exception as e:
        log_message(f"❌ 파일 분석 오류: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start', methods=['POST'])
def start():
    """자동화 시작"""
    global current_task
    
    if current_task['is_running']:
        return jsonify({'success': False, 'error': '이미 실행 중입니다.'})
    
    if not current_task['links']:
        return jsonify({'success': False, 'error': '먼저 링크를 분석해주세요.'})
    
    data = request.json
    button_selector = data.get('button_selector', 'button')
    delay = data.get('delay', 3)
    
    # 새 스레드에서 자동화 실행
    thread = threading.Thread(
        target=run_automation, 
        args=(current_task['links'], button_selector, delay)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True})

@app.route('/stop', methods=['POST'])
def stop():
    """자동화 중지"""
    stop_automation()
    return jsonify({'success': True})

@app.route('/status')
def status():
    """현재 상태 반환"""
    return jsonify({
        'is_running': current_task['is_running'],
        'progress': current_task['progress'],
        'total': current_task['total'],
        'logs': current_task['logs']
    })

if __name__ == '__main__':
    log_message("🌐 웹 서버 시작됨!")
    log_message("👉 브라우저에서 http://localhost:8080 으로 접속하세요!")
    app.run(debug=True, port=8080, host='0.0.0.0') 