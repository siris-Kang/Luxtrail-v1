from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Hello, FastAPI!</h1><p>서버 잘 뜬다 🎉</p>"

# uvicorn main:app --reload
# http://localhost:8000