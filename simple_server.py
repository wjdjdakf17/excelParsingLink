from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎉 드디어 성공했습니다!</h1>
    <h2>🚀 링크 자동 클릭 프로그램이 작동 중입니다!</h2>
    <p>이제 제대로 작동합니다!</p>
    <button onclick="alert('버튼 클릭됨!')">테스트 버튼</button>
    '''

if __name__ == '__main__':
    print("🌐 간단한 테스트 서버 시작!")
    print("👉 브라우저에서 http://localhost:9999 로 접속하세요!")
    app.run(debug=True, port=9999, host='0.0.0.0') 