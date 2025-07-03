#!/usr/bin/env python3
"""
간단한 웹훅 테스트 서버
포트 8000에서 실행되며 모든 요청을 로깅합니다.
"""

from flask import Flask, request, jsonify
import json
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🧪 웹훅 테스트 서버</h1>
    <p>서버가 정상적으로 실행 중입니다!</p>
    <p>현재 시간: {}</p>
    <hr>
    <h3>테스트 방법:</h3>
    <p>POST 요청을 <code>/webhook/tradingview</code>로 보내세요</p>
    <p>예시: <code>curl -X POST http://서버IP/webhook/tradingview -d '{{"test":"message"}}'</code></p>
    """.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/webhook/tradingview', methods=['GET', 'POST'])
def webhook_test():
    print("\n" + "="*50)
    print(f"🔔 웹훅 수신! - {datetime.datetime.now()}")
    print("="*50)
    
    # 요청 정보 출력
    print(f"📍 Method: {request.method}")
    print(f"📍 IP: {request.remote_addr}")
    print(f"📍 URL: {request.url}")
    print(f"📍 Headers: {dict(request.headers)}")
    
    # GET 요청 처리
    if request.method == 'GET':
        print("📍 GET 요청 - 테스트 페이지 반환")
        return """
        <h1>✅ 웹훅 엔드포인트 작동 중!</h1>
        <p>이 페이지가 보인다면 웹훅 엔드포인트가 정상적으로 작동합니다.</p>
        <p>POST 요청으로 실제 웹훅을 테스트하세요.</p>
        """
    
    # POST 요청 처리
    try:
        # Raw 데이터 확인
        raw_data = request.get_data(as_text=True)
        print(f"📍 Raw Data: {raw_data}")
        
        # JSON 파싱 시도
        if raw_data:
            try:
                json_data = json.loads(raw_data)
                print(f"📍 JSON Data: {json.dumps(json_data, indent=2)}")
            except:
                print(f"📍 JSON 파싱 실패, Raw 데이터로 처리")
                json_data = {"raw": raw_data}
        else:
            json_data = {"message": "빈 데이터"}
        
        # 성공 응답
        response = {
            "status": "success", 
            "message": "웹훅이 성공적으로 수신되었습니다!",
            "timestamp": datetime.datetime.now().isoformat(),
            "received_data": json_data
        }
        
        print(f"📍 응답: {json.dumps(response, indent=2)}")
        print("="*50 + "\n")
        
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        print("="*50 + "\n")
        
        return jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

@app.route('/test')
def test():
    """간단한 테스트 엔드포인트"""
    return jsonify({
        "message": "테스트 성공!",
        "timestamp": datetime.datetime.now().isoformat(),
        "server": "Test Webhook Server"
    })

if __name__ == '__main__':
    print("\n🚀 웹훅 테스트 서버 시작!")
    print("📍 포트: 8000")
    print("📍 웹훅 URL: http://서버IP:8000/webhook/tradingview")
    print("📍 테스트 URL: http://서버IP:8000/test")
    print("📍 종료: Ctrl+C")
    print("\n" + "="*50)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
