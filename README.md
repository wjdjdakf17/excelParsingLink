# 🚀 Excel Link Auto Clicker - 완전 자동화 시스템

친구가 **브라우저에서 바로** 완전 자동화를 실행할 수 있는 시스템입니다!

## 🎯 **친구용 사용법 (5분 완성!)**

### 🌐 **방법 1: GitHub Codespaces (무료 + 추천)**

1. **GitHub 계정 만들기** (무료)

   - https://github.com 접속
   - **Sign up** 클릭
   - 이메일, 비밀번호 입력

2. **이 링크 클릭** 👉 **https://github.com/wjdjdakf17/excelParsingLink**

3. **초록색 "Code" 버튼** 클릭 → **"Codespaces"** 탭 → **"Create codespace on main"**

4. **브라우저에서 VS Code가 자동 실행됨** (약 2-3분 소요)

5. **터미널에서 명령어 실행**:

   ```bash
   cd link-auto-click
   python3 web_app.py
   ```

6. **포트 8080 자동 공개** → 링크 클릭하면 웹페이지 열림!

7. **Excel 파일 업로드** → **자동화 실행** 🎉

---

### 🖥️ **방법 2: Vercel (링크 분석만)**

**현재 링크**: https://excel-parsing-link.vercel.app/

- ✅ **Excel 파일 분석**
- ✅ **링크 추출 및 버튼 감지**
- ❌ **실제 자동 클릭** (서버리스 제약)

---

## 🔧 **로컬 실행 (고급 사용자)**

### 필수 조건

- Python 3.9+
- Chrome 브라우저
- ChromeDriver

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/wjdjdakf17/excelParsingLink.git
cd excelParsingLink/link-auto-click

# 패키지 설치
pip install -r requirements.txt

# Chrome Remote Debugging 모드 시작
open -a "Google Chrome" --args --remote-debugging-port=9222

# 웹앱 실행
python3 web_app.py
```

**브라우저에서 접속**: http://localhost:8080

---

## 🎯 **자동화 기능**

### ✨ **지원 기능**

- 📊 **Excel 파일 분석** (.xlsx, .xls)
- 🔗 **링크 자동 추출**
- 🤖 **자동 로그인** (ID: paranormal, PW: wotjd214!@)
- 🎯 **스마트 버튼 클릭**
- 📈 **실시간 진행 상황 모니터링**

### 🎯 **타겟 버튼**

- `#update_start` (ID)
- 텍스트: "상품업데이트 & 마켓전송 시작"
- 기타 일반적인 버튼 패턴

---

## 📱 **사용 방법**

1. **Excel 파일 준비** (링크가 포함된 .xlsx 또는 .xls)
2. **파일 업로드**
3. **📊 링크 분석** 클릭
4. **🚀 자동화 시작** 클릭
5. **실시간 로그 확인**
6. **완료까지 대기** ☕

---

## 🆘 **문제 해결**

### Chrome 연결 오류

```bash
# 기존 Chrome 프로세스 종료
pkill -f "Google Chrome"

# Chrome Remote Debugging 모드 재시작
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-remote-debug
```

### 패키지 설치 오류

```bash
# Python 버전 확인
python3 --version

# 패키지 재설치
pip3 install --upgrade -r requirements.txt
```

---

## 📋 **시스템 요구사항**

### GitHub Codespaces

- ✅ **무료** (월 120시간)
- ✅ **브라우저만 있으면 됨**
- ✅ **자동 환경 설정**
- ✅ **외부 접속 자동 지원**

### 로컬 환경

- 🖥️ **macOS/Windows/Linux**
- 🐍 **Python 3.9+**
- 🌐 **Chrome 브라우저**
- 🔧 **ChromeDriver**

---

## 🚀 **고급 기능**

### 자동 로그인 설정

- **기본 계정**: paranormal / wotjd214!@
- **커스텀 설정**: `web_app.py` 파일에서 수정 가능

### 버튼 선택자 커스터마이징

```python
# web_app.py 파일에서 수정
button_selectors = [
    "#update_start",
    "button[class*='update']",
    "input[value*='시작']"
]
```

---

## 📞 **지원**

문제가 있으면 GitHub Issues에 올려주세요!

- **GitHub Issues**: https://github.com/wjdjdakf17/excelParsingLink/issues

---
