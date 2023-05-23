from flask import Flask, render_template, request
import requests

app = Flask(__name__)
_id = ''
_pw = ''
_upTime = ''
_downTime = ''
_upSeat = ''
_downSeat = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST' :
        global _id, _pw, _upTime, _downTime, _upSeat, _downSeat
        _id = request.form['_id']
        _pw = request.form['_pw']
        _upTime = request.form['_upTime']
        _downTime = request.form['_downTime']
        _upSeat = request.form['_upSeat']
        _downSeat = request.form['_downSeat']
        _option = request.form.get('option')

        if _option == 'a':
            # run()
            return "a"
        elif _option == 'b' :
            return "b"
        else:
            return "신청 방법을 선택해주세요"

        return f'{_id}, {_pw}, {_upTime}, {_downTime}, {_upSeat}, {_downSeat}, {_option}'
    else :
        return render_template('index.html')

def run():
    # 로그인 데이터
    loginData = {
        "id": _id,
        "pass": _pw,
        "autoLogin": ""
    }
    # 로그인 요청 URL
    loginUrl = "https://daejin.unibus.kr/api/index.php?ctrl=Main&action=loginProc"

    # 버스예약 요청 URL
    reserveUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=reserveAppProc"

    # 버스 리스트 url (노원하교)
    busListDownUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=busList&dir=DOWN&lineGroupSeq=27"

    # 버스 리스트 url (노원등교)
    busListUpUrl = "https://daejin.unibus.kr/api/index.php?ctrl=BusReserve&action=busList&dir=UP&lineGroupSeq=28"

    session = requests.Session()
    response = session.post(loginUrl, json=loginData)
    if "OK" in response.text:
        print("로그인 성공")
        print("응답코드 = " + str(response.status_code))
        cookie = response.cookies.get_dict()
        print(cookie)
        print(type(cookie))

        # 로그인후 Authorization을 가져오기
        # {'result': 'OK', 'resultMsg': '', 'data': 'QedXyA83JFEG8nl8zeoM3mD693G7wbSFxu3lAgFeziWjPnRXcx+X5hECB2QZo3CB85wNBVHVcgOiU6W15FWH6g=='}
        response_json = response.json()
        token = response_json.get('data')
        header = {
            "Authorization": token
        }
        if token:
            # 하교(노원) 버스리스트 가져오기
            busDownResponse = session.get(busListDownUrl, cookies=cookie, headers=header)
            if busDownResponse.status_code == 200:
                downData = busDownResponse.json()
                print(downData)
                for data in downData['data']['busList']:
                    # 하교 버스 시간 설정
                    if data['operateTime'] == _downTime:
                        downBusSeq = (data['busSeq'])
            else:
                print("하교 리스트 가져오기 실패")

            # 등교(노원) 버스리스트 가져오기
            busUpResponse = session.get(busListUpUrl, cookies=cookie, headers=header)
            if busUpResponse.status_code == 200:
                upData = busUpResponse.json()
                for data in upData['data']['busList']:
                    # 등교 버스 시간 설정
                    if data['operateTime'] == _upTime:
                        upBusSeq = (data['busSeq'])
            else:
                print("등교 리스트 가져오기 실패")
        else:
            print('로그인 실패! 인증 토큰이 없습니다.')

        # 하교 버스 데이터
        # 노원 lineSeq - 27 / stopSeq - 77
        # 마들 line Seq - 27 / stopSeq - 78
        # 수락산역 lineSeq - 27 / stopSeq - 79
        try:
            downReserveData = {
                "busSeq": downBusSeq,  # 버스번호
                "lineSeq": "27",  # 버스노선노원하교: 27 / 하계등교: 33
                "stopSeq": 77,  # 하차위치노원하교: 77 / 하계등교 : ??
                "seatNo": int(_downSeat)  # 좌석번호
            }
        except NameError:
            pass

        # 등교 버스 데이터
        # 태릉 lineSeq - 32 / stopSeq - 112
        # 중화 lineSeq - 31 / stopSeq - 106
        # 노원 lineSeq - 28 / stopSeq - 80
        # 하계 lineSeq - 33 / stopSeq - 113
        # 등교 위치가 변경될 경우 busListUpUrl의 맨 마지막 lineGroupSeq=28의 숫자도 lineSeq값으로 변경해야댐
        try:
            upReserveData = {
                "busSeq": upBusSeq,
                "lineSeq": "28",
                "stopSeq": 80,
                "seatNo": int(_upSeat)  # 좌석번호
            }
        except NameError:
            pass
        # 등교 버스 예약 ㄱㄱ
        try:
            busUpReserve = session.post(reserveUrl, cookies=cookie, headers=header, json=upReserveData)
        except NameError:
            pass
        # 하교 버스 예약 ㄱㄱ
        try:
            busDownReserve = session.post(reserveUrl, cookies=cookie, headers=header, json=downReserveData)
        except NameError:
            pass
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        print("result 값이 OK면 성공")
        try:
            print("등교 내역 = " + str(busUpReserve.json()))
        except NameError:
            pass
        try:
            print("하교 내역 = " + str(busDownReserve.json()))
        except NameError:
            pass
    else:
        print("로그인 실패")
        print(response.text)




if __name__ == '__main__':
    app.run(debug=True, port=8080)
