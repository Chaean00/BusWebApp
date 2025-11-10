# BusWebApp





<img width="428" height="900" alt="image" src="https://github.com/user-attachments/assets/a734e44e-eddb-4b85-bd4d-02fa7b09449c" />


## 소개
> 대학 통학 셔틀버스 예약 웹 애플리케이션<br/>
수동으로 로그인하여 좌석을 예약하는 대신, 사용자는 본인의 정보를 입력하고 즉시 또는 예약된 시간에 자동으로 예약이 처리되도록 할 수 있습니다.

<br>

## 주요 기능
**즉시 예약:** 버스 좌석을 즉시 예약합니다.

**예약된 예약:** 매일 밤 10시에 자동으로 예약이 실행되도록 설정할 수 있습니다.

**간단한 UI:** 예약 세부 정보를 입력하기 위한 사용하기 쉬운 인터페이스를 제공합니다.

<br>

## 실행 방법

1.  **저장소 복제:**
    ```bash
    git clone https://github.com/Chaean00/BusWebApp.git
    ```

2.  **가상 환경 생성 및 활성화:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Flask 애플리케이션 실행:**
    ```bash
    flask --app app:app run --host=0.0.0.0 --port=8000
    # 만약 8000번 포트를 사용하고있을 시 5000,8080 등 사용하지 않는 포트로 실행
    ```

5.  **웹 브라우저를 열고 `http://127.0.0.1:8000`으로 이동합니다.**




## 의존성

이 프로젝트에서 사용되는 주요 의존성은 다음과 같습니다:

-   Flask
-   requests
-   APScheduler

전체 의존성 목록은 `requirements.txt`를 참조하세요.
