import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import time

# To avoid Detection of BJ
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Connection": "keep-alive"
}

kst = timezone(timedelta(hours=9))
now_kst = datetime.now(kst)

def get_today_accepted_problems(user_id: str, date: str):
    problems = set()
    url = f"https://www.acmicpc.net/status?user_id={user_id}"

    with httpx.Client(headers=headers) as client:
        for page in range(1, 2):
            try:
                # 페이지를 넘기는 동안 연결 유지 - get
                response = client.get(url + f"&page={page}", follow_redirects=True)
                response.raise_for_status() # !(200 OK) -> HTTPStatusError

                # To avoid detection: check 403 error
                if "403 Forbidden" in response.text:
                    print(f"ERROR: {page} page -  There is '403 Forbidden' error in the page")
                elif not response.text.strip():
                    print(f"ERROR: {page} page - 텍스트가 비어있어요.")
                else:
                    print(f"DEBUG: Connection is Good...")


                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table tbody tr")

                if len(rows) == 0:
                    print(f"DEBUG: {page} page - row가 0입니다.")
                    time.sleep(1)
                    continue

                for i, row in enumerate(rows):
                    cols = row.find_all("td")

                    # get Date info
                    time_td = cols[8]
                    time_tag = time_td.find("a", class_="real-time-update")
                    if time_tag is None:
                        print(f"DEBUG: Row {i} (page {page}): Can not find time-tag from 'real-time-update'")
                        continue

                    # BeautifulSoup / httpx는 정적 HTML만 가져옴 - 그래서 time stamp 사용
                    timestamp_str = time_tag.get("data-timestamp", "")
                    if not timestamp_str:
                        continue

                    try:
                        timestamp = int(timestamp_str)

                        submit_date = datetime.fromtimestamp(timestamp, tz=kst).date()
                        if submit_date != now_kst.date():
                            continue
                        
                        # timestamp 값이 오늘 날짜와 일치하는 경우
                        result_td = cols[3]
                        result_span = result_td.find("span")
                        if not result_span or "맞았습니다!!" not in result_span.text:
                            continue
                        
                        # 맞은 문제 리스트에 추가
                        problem_id = cols[2].text.strip()
                        problems.add(problem_id)

                    except Exception as e:
                        continue

            except httpx.HTTPStatusError as e: # 4xx or 5xx error 시 다음 페이지로
                print(f"ERROR: {page} page -  HTTP 상태 오류: {e.response.status_code} - {e.response.text[:200]}...")
                continue

            time.sleep(1) 

    return list(problems)


def get_solvedac_user_info(username):
    url = f"https://solved.ac/profile/{username}"
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status() # Error Catch

        soup = BeautifulSoup(response.text, "html.parser")

        # 프로필 이미지 가져오기
        profile_img_tag = soup.find("img", {"alt": username})
        profile_img = profile_img_tag["src"] if profile_img_tag else None
    
    except httpx.HTTPStatusError as e: # 4xx or 5xx error 시 다음 페이지로
        print(f"ERROR: HTTP state error: {e.response.status_code} - {e.response.text[:200]}...")

    return profile_img
    
