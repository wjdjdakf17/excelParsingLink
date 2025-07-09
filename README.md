# 🚀 링크 자동 클릭 프로그램

엑셀 파일에서 링크를 자동으로 추출하고 지정된 버튼을 자동으로 클릭하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- 📁 **엑셀 파일 업로드**: .xlsx, .xls 파일 지원
- 📊 **자동 링크 분석**: 모든 시트에서 HTTP 링크 자동 추출
- 🎯 **스마트 버튼 클릭**: ID, 클래스, 태그명으로 버튼 지정
- 📈 **실시간 모니터링**: 진행 상황과 로그를 실시간으로 확인
- 🎮 **완전한 제어**: 언제든지 시작/중지 가능

## 🛠️ 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **자동화**: Selenium WebDriver
- **데이터 처리**: Pandas, OpenPyXL

## 🚀 로컬 실행 방법

### 1. 저장소 클론

```bash
git clone https://github.com/wjdjdakf17/excelParsingLink.git
cd excelParsingLink
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Chrome Driver 설정

- [ChromeDriver 다운로드](https://chromedriver.chromium.org/)
- `chromedriver-mac-arm64/chromedriver` 경로에 배치

### 4. 서버 실행

```bash
python web_app.py
```

### 5. 브라우저에서 접속

```
http://localhost:8080
```

## 📖 사용법

1. **📁 엑셀 파일 선택**: 링크가 포함된 엑셀 파일 업로드
2. **📊 링크 분석**: "링크 분석" 버튼으로 모든 링크 추출
3. **🎯 버튼 설정**: 클릭할 버튼 지정
   - `#update_start` (ID로 찾기)
   - `.btn` (클래스로 찾기)
   - `button` (태그명으로 찾기)
4. **🚀 자동화 시작**: 모든 링크에 자동으로 접속하여 버튼 클릭

## 🎯 버튼 선택자 예시

| 타입   | 예시            | 설명                        |
| ------ | --------------- | --------------------------- |
| ID     | `#update_start` | id="update_start"인 요소    |
| 클래스 | `.defBtn`       | class="defBtn"인 요소       |
| 태그   | `button`        | 모든 button 태그            |
| 텍스트 | `text:시작`     | "시작" 텍스트를 포함한 요소 |

## 📸 스크린샷

![메인 화면](screenshot.png)

## 🔒 주의사항

- Chrome Driver가 시스템에 설치되어 있어야 합니다
- 대량의 링크 처리 시 웹사이트 서버에 부하를 줄 수 있으니 적절한 딜레이를 설정해주세요
- 자동화 대상 웹사이트의 이용약관을 확인해주세요

## 🤝 기여하기

1. Fork 하기
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 🆘 문제 해결

### Chrome Driver 오류

```bash
# macOS에서 권한 오류 시
chmod +x chromedriver-mac-arm64/chromedriver
```

### 포트 충돌

```bash
# 다른 포트로 실행
python web_app.py --port 9999
```

---

**💡 만든이**: 링크 자동화의 혁신을 꿈꾸는 개발자
