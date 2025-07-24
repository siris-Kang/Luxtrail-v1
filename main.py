from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import time # time 모듈 import
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 *로 열어두기
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# To avoid Detection of Backjoon site
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Connection": "keep-alive"
}

# Time information, KST (UTC + 9h)
kst = timezone(timedelta(hours=9))
now_kst = datetime.now(kst)

today = now_kst.strftime("%Y-%m-%d") # "YYYY-MM-DD" [Delete]


def get_today_accepted_problems(user_id: str, date: str):
    problems = set()
    url = f"https://www.acmicpc.net/status?user_id={user_id}"
    print(f"DEBUG: 사용자: {user_id}, 검색 날짜: {date}")

    with httpx.Client(headers=headers) as client:
        for page in range(1, 2):
            try:
                response = client.get(url + f"&page={page}", follow_redirects=True)
                response.raise_for_status() # 200 OK가 아니면 HTTPStatusError 발생

                # To avoid detection: check 403 error
                if "403 Forbidden" in response.text:
                    print(f"ERROR: {page} **There is '403 Forbidden' error in the page")
                elif not response.text.strip():
                    print(f"ERROR: {page} **페이지에서 응답 텍스트가 비어있거나 공백만 있습니다!")
                else:
                    print(f"DEBUG: {page} **페이지의 응답 HTML (일부): {response.text[:500]}...")


                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table tbody tr")
                print(f"DEBUG: {page} 페이지에서 총 {len(rows)}개의 행(row) 발견.")

                if len(rows) == 0:
                    print(f"DEBUG: {page} 페이지에 유효한 제출 행이 없습니다. 다음 페이지로 이동합니다.")
                    time.sleep(1)
                    continue

                for i, row in enumerate(rows):
                    cols = row.find_all("td")
                    
                    if len(cols) < 9:
                        # print(f"DEBUG: Row {i} (페이지 {page}): 컬럼 수가 9개 미만입니다 ({len(cols)}개).")
                        continue

                    # get Date info
                    time_td = cols[8]
                    time_tag = time_td.find("a", class_="real-time-update")
                    if time_tag is None:
                        print(f"DEBUG: Row {i} (페이지 {page}): Can not find time-tag from 'real-time-update'")
                        continue

                    # raw_date = time_tag.get("data-original-title", "")
                    # BeautifulSoup / httpx는 정적 HTML만 가져옴
                    timestamp_str = time_tag.get("data-timestamp", "") # 그래서 time stamp 사용
                    if not timestamp_str:
                        continue

                    try:
                        timestamp = int(timestamp_str)

                        submit_date = datetime.fromtimestamp(timestamp, tz=kst).date()
                        if submit_date != now_kst.date():
                            continue
                        result_td = cols[3]
                        result_span = result_td.find("span")
                        if not result_span or "맞았습니다!!" not in result_span.text:
                            continue
                        
                        # 맞은 문제 리스트에 추가
                        problem_id = cols[2].text.strip()
                        problems.add(problem_id)

                    except Exception as e:
                        continue


            
            except httpx.HTTPStatusError as e:
                print(f"ERROR: {page} 페이지에서 HTTP 상태 오류 발생: {e.response.status_code} - {e.response.text[:200]}...")
                # 4xx 또는 5xx 오류 발생 시 다음 페이지로 진행
            except httpx.RequestError as e:
                print(f"ERROR: {page} 페이지 요청 중 네트워크 오류 발생: {e}")

            time.sleep(1) 

    print(f"DEBUG: 검색 완료. 최종 찾은 문제들: {list(problems)}")
    return list(problems)

def get_solvedac_user_info(username):
    url = f"https://solved.ac/profile/{username}"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Connection": "keep-alive"
    }

    res = httpx.get(url, headers=headers)

    if res.status_code != 200:
        print("요청 실패:", res.status_code)
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    # 프로필 이미지 찾기 (alt=유저 이름인 img)
    profile_img_tag = soup.find("img", {"alt": username})
    profile_img = profile_img_tag["src"] if profile_img_tag else None

    return profile_img


@app.get("/submissions/{user_id}")
def get_today(user_id: str):
    problems = get_today_accepted_problems(user_id, today)
    user_img = get_solvedac_user_info(user_id)
    return {"date": today, "user": user_id, "problems": problems, "profileImg": user_img}

