from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time # time 모듈 import

app = FastAPI()

# 💡 봇 감지를 피하기 위한 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Connection": "keep-alive"
}

def get_today_accepted_problems(user_id: str, date: str):
    problems = set()
    url = f"https://www.acmicpc.net/status?user_id={user_id}"
    print(f"DEBUG: 사용자: {user_id}, 검색 날짜: {date}")

    with httpx.Client(headers=headers) as client:
        # 최근 3페이지만 확인합니다. (필요시 range 범위 조정)
        for page in range(1, 4):
            print(f"\nDEBUG: {page} 페이지 확인 중...") # 페이지 구분을 위해 줄바꿈 추가
            try:
                response = client.get(url + f"&page={page}", follow_redirects=True)
                response.raise_for_status() # 200 OK가 아니면 HTTPStatusError 발생

                # 응답 HTML 내용 요약 출력 (403 에러가 사라졌는지 확인)
                if "403 Forbidden" in response.text:
                    print(f"ERROR: {page} 페이지에서 여전히 '403 Forbidden' 에러가 감지됩니다.")
                elif not response.text.strip(): # 공백만 있는 경우도 확인
                    print(f"ERROR: {page} 페이지에서 응답 텍스트가 비어있거나 공백만 있습니다!")
                else:
                    print(f"DEBUG: {page} 페이지의 응답 HTML (일부): {response.text[:500]}...")

                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table tbody tr")
                print(f"DEBUG: {page} 페이지에서 총 {len(rows)}개의 행(row) 발견.")

                if len(rows) == 0:
                    print(f"DEBUG: {page} 페이지에 유효한 제출 행이 없습니다. 다음 페이지로 이동합니다.")
                    time.sleep(1) # 행이 없어도 다음 페이지로 넘어가기 전 지연
                    continue

                for i, row in enumerate(rows):
                    cols = row.find_all("td")
                    
                    # 최소한의 컬럼 수 확인 (테이블 구조 변경 대비)
                    if len(cols) < 9:
                        # print(f"DEBUG: Row {i} (페이지 {page}): 컬럼 수가 9개 미만입니다 ({len(cols)}개). 건너뜝니다.")
                        continue

                    # 제출 결과: '맞았습니다!!' 인지 확인
                    result_td = cols[3]
                    result_span = result_td.find("span")
                    
                    if not result_span:
                        # print(f"DEBUG: Row {i} (페이지 {page}): 결과 span 태그를 찾을 수 없습니다. 건너뜝니다.")
                        continue
                    
                    result_text = result_span.text.strip()
                    # print(f"DEBUG: Row {i} (페이지 {page}): 결과 텍스트: '{result_text}'")
                    if "맞았습니다!!" not in result_text:
                        # print(f"DEBUG: Row {i} (페이지 {page}): 결과가 '맞았습니다!!'가 아닙니다. 건너뜝니다.")
                        continue

                    # 날짜 추출
                    time_td = cols[8]
                    time_tag = time_td.find("a", class_="real-time-update")
                    if time_tag is None:
                        print(f"DEBUG: Row {i} (페이지 {page}): 'real-time-update' 클래스의 시간 태그를 찾을 수 없습니다. 건너뜝니다.")
                        continue

                    raw_date = time_tag.get("data-original-title", "")
                    print(f"DEBUG: Row {i} (페이지 {page}): 추출된 raw_date (data-original-title): '{raw_date}'")
                    if not raw_date:
                        print(f"DEBUG: Row {i} (페이지 {page}): raw_date가 비어있습니다. 건너뜝니다.")
                        continue

                    try:
                        # 'YYYY년MM월DD일' 부분만 추출하여 파싱
                        date_part = raw_date.split()[0]
                        submit_date = datetime.strptime(date_part, "%Y년%m월%d일").date()
                        
                        # 💡 핵심 디버깅 출력: 파싱된 제출 날짜와 목표(오늘) 날짜 비교 결과
                        print(f"DEBUG: Row {i} (페이지 {page}): 파싱된 제출 날짜: {submit_date.strftime('%Y-%m-%d')}, 목표(오늘) 날짜: {date}")
                        
                        if submit_date.strftime("%Y-%m-%d") != date:
                            print(f"DEBUG: Row {i} (페이지 {page}): 날짜가 일치하지 않습니다 ({submit_date.strftime('%Y-%m-%d')} != {date}). 건너뜁니다.")
                            continue
                        else:
                            print(f"DEBUG: Row {i} (페이지 {page}): **날짜가 일치합니다! ({submit_date.strftime('%Y-%m-%d')} == {date})**")

                        # 문제 번호 추출
                        problem_id = cols[2].text.strip()
                        print(f"DEBUG: Row {i} (페이지 {page}): **오늘 맞은 문제 발견 (문제 번호): {problem_id}**")
                        problems.add(problem_id)

                    except ValueError as e:
                        print(f"DEBUG: Row {i} (페이지 {page}): 날짜 파싱 중 오류 발생 ('{raw_date}'): {e}. 이 행은 건너뜁니다.")
                        continue
            
            except httpx.HTTPStatusError as e:
                print(f"ERROR: {page} 페이지에서 HTTP 상태 오류 발생: {e.response.status_code} - {e.response.text[:200]}...")
                # 4xx 또는 5xx 오류 발생 시 다음 페이지로 진행
            except httpx.RequestError as e:
                print(f"ERROR: {page} 페이지 요청 중 네트워크 오류 발생: {e}")
                # 네트워크 오류 발생 시 다음 페이지로 진행

            # 💡 각 페이지 요청 후 1초 지연 (Rate Limiting 회피)
            time.sleep(1) 

    print(f"DEBUG: 검색 완료. 최종 찾은 문제들: {list(problems)}")
    return list(problems)


@app.get("/submissions/{user_id}")
def get_today(user_id: str):
    # KST (UTC + 9시간)으로 현재 날짜 계산
    now_kst = datetime.utcnow() + timedelta(hours=9)
    today = now_kst.strftime("%Y-%m-%d") # "YYYY-MM-DD" 형식

    print(f"\nDEBUG: 요청에 대한 현재 KST 날짜: {today}") # 시작 시 현재 날짜 출력
    problems = get_today_accepted_problems(user_id, today)
    return {"date": today, "user": user_id, "problems": problems}