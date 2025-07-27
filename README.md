## LuxTrail (Ver. 1)

Check friends' streaks on Baekjoon
  
본 프로젝트는 백준 사이트의 **크롤링 기반**으로 작동하므로  
지속적인 사용은 권장되지 않습니다.
  
  
크롤링은 서버에 좋지 않고  
IP가 차단될 수 있다는 피드백을 받아 프로젝트를 중단하였습니다.
  
  
---

### 프로젝트 동기

스터디장으로서 알고리즘 스터디를 진행하려다보니  
스터디원들이 오늘 문제를 풀었는지 여부를 매번 직접 묻거나 확인해야하는 작업이 불편하였다.  
또한, 오늘 다 같이 풀기로 한 문제를 풀었는지도 확인하여야했기에 불편함이 두배였다.  
  
마침 이번주에 웹을 처음으로 배우게 되었고  
이전에 웹페이지 크롤링을 해 본 경험도 있었기에  
fastAPI로 프론트에서 요청 받아오는 부분만 연동하여 페이지를 만들었다.  
  
**한 페이지에서 모든 정보를 확인하고 싶다!**
  
  
---

###  페이지 기능 구성

#### 1. 유저 스트릭 정보 확인

* 유저가 **오늘 문제를 풀었는지 여부** 표시
* **푼 문제 개수**와
* **푼 문제 번호 목록** 확인 가능
* solved.ac에서 유저 **프로필 이미지도 포함**

#### 2. 특정 문제 풀이 여부 확인

* 문제 번호를 입력하면,
* **여러 유저가 그 문제를 풀었는지 여부를 한 번에 표시**
* ✅ 풀었음 / ❌ 안풀었음을 간단히 확인 가능
  
  
---

### 설치 및 실행 방법

#### Python 환경 설정

```bash
python -m venv luxtrail
luxtrail\Scripts\activate  # Linux / macOS: source luxtrail/bin/activate
pip install -r requirements.txt
```

> fastapi  
> uvicorn  
> httpx  
> beautifulsoup4  

VSCode Extensions
> Live Server
  
  
#### 전체 실행 순서

1. `main.py` 실행 (FastAPI 서버 실행)
2. `index.html`에서 우클릭 -> Open with Live Server
3. 웹페이지에서:
   * 유저 계정을 컴마(,)로 구분해 입력 -> GET
   * 문제 번호 입력 -> 문제 체크
---

### 사용 예시 화면

(images/example.png)
  
  
---

### 디렉터리 구조

```Luxtrail
├── main.py
├── get_user_info.py
├── templates
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── README.md
```

