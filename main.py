from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from get_user_info import get_today_accepted_problems, get_solvedac_user_info
import uvicorn

app = FastAPI()

# CORS 설정
# 다른 도메인/포트에서도 API 요청 가능하도록
# 없으면 fetch 요청이 막힌다
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Time information, KST (UTC+9h)
kst = timezone(timedelta(hours=9))
now_kst = datetime.now(kst)
today = now_kst.strftime("%Y-%m-%d")


@app.get("/submissions/{user_id}")
def get_today(user_id: str):
    problems = get_today_accepted_problems(user_id, today)
    user_img = get_solvedac_user_info(user_id)
    return {
        "date": today,
        "user": user_id,
        "problems": problems,
        "profileImg": user_img
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
