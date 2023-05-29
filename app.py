from flask import Flask, render_template, request, jsonify
import requests
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
upReserveText = ''
downReserveText = ''
resultMsg = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fail')
def fail():
    return render_template('fail.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST' :
        _id = request.form.get('_id')
        _pw = request.form.get('_pw')
        _upTime = request.form.get('_upTime')
        _downTime = request.form.get('_downTime')
        _upSeat = request.form.get('_upSeat')
        _downSeat = request.form.get('_downSeat')
        _option = request.form.get('option')
        response = {'message' : ''}
        # 일반 신청
        if _option == 'a':
            if _upTime != '':
                if _upSeat == '':
                    response['message'] = '등교 좌석이 입력되어있지 않습니다.'
                    return jsonify(response)
                else :
                    if (int(_upSeat) < 1) or (int(_upSeat) > 44):
                        response['message'] = '존재하지않는 좌석 번호 입니다.'
                        return jsonify(response)
            if _downTime != '':
                if _downSeat == '':
                    response['message'] = '하교 좌석이 입력되어있지 않습니다.'
                    return jsonify(response)
                else :
                    if (int(_downSeat) < 1) or (int(_downSeat) > 44):
                        response['message'] = '존재하지않는 좌석 번호 입니다.'
                        return jsonify(response)
            if _upSeat != '':
                if _upTime == '':
                    response['message'] = '등교 시간이 입력되어있지 않습니다'
                    return jsonify(response)
            if _downSeat !='':
                if _downTime == '':
                    response['message'] = "하교 시간이 입력되어있지 않습니다."
                    return jsonify(response)

            run(_id=_id, _pw=_pw, _upTime=_upTime, _downTime=_downTime, _upSeat=_upSeat, _downSeat=_downSeat)
            if ("OK" == upReserveText) or ("OK" == downReserveText):
                response['message'] = '정상적으로 처리되었습니다.'
                return jsonify(response)
            else:
                response['message'] = resultMsg
                return jsonify(response)

        # 예약 신청
        elif _option == 'b':
            if _upTime != '':
                if _upSeat == '':
                    response['message'] = '등교 좌석이 입력되어있지 않습니다.'
                    return jsonify(response)

            if _downTime != '':
                if _downSeat == '':
                    response['message'] = '하교 좌석이 입력되어있지 않습니다.'
                    return jsonify(response)

            if _upSeat != '':
                if _upTime == '':
                    response['message'] = '등교 시간이 입력되어있지 않습니다'
                    return jsonify(response)
            if _downSeat !='':
                if _downTime == '':
                    response['message'] = "하교 시간이 입력되어있지 않습니다."
                    return jsonify(response)
            schedule_job(_id=_id, _pw=_pw, _upTime=_upTime, _downTime=_downTime, _upSeat=_upSeat, _downSeat=_downSeat)
            response['message'] = '예약을 완료했습니다.'
            return jsonify(response)

        # 아무것도 안눌렀을 때
        else:
            response = {'message': '신청 버튼을 눌러주세요'}
            return jsonify(response)


    else :
        return render_template('index.html')

def run(_id, _pw, _upTime, _downTime, _upSeat, _downSeat):
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
        global upReserveText, downReserveText, resultMsg
        print("로그인 성공")
        print("응답코드 = " + str(response.status_code))
        cookie = response.cookies.get_dict()

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
            upReserveText = busUpReserve.json()['result']
            print("등교 내역 = " + str(busUpReserve.json()))
            if upReserveText == "FAIL":
                resultMsg = busUpReserve.json()['resultMsg']
        except NameError:
            pass
        try:
            downReserveText = busDownReserve.json()['result']
            print("하교 내역 = " + str(busDownReserve.json()))
            if downReserveText == "FAIL":
                resultMsg = busUpReserve.json()['resultMsg']
        except NameError:
            pass
    # return
    else:
        print("로그인 실패")
        print(response.text)
def schedule_job(_id, _pw, _upTime, _downTime, _upSeat, _downSeat):

    job_id = f'{_id}_bus_reserve'
    job_date = datetime.today().replace(hour=1, minute=13, second=00)

    if job_date < datetime.now():  # 오늘 22시 1초가 이미 지났다면 내일 22시 1초로 설정
        job_date += timedelta(days=1)

    for job in scheduler.get_jobs():
        if job.id == job_id:
            scheduler.remove_job(job_id)

    scheduler.add_job(run, 'date', run_date=job_date, id=job_id, args=[_id, _pw, _upTime, _downTime, _upSeat, _downSeat])
    print(scheduler.get_jobs())
    if not scheduler.running:
        scheduler.start()

if __name__ == '__main__':
    app.run(port=8080, debug=True)
