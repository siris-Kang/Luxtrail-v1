import httpx
from bs4 import BeautifulSoup

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

    # 티어 이미지 찾기
    tier_img_tag = soup.find("img", {"alt": lambda val: val and "tier" in val.lower()})
    tier_img = tier_img_tag["src"] if tier_img_tag else None

    # 링크는 username으로 직접 만들 수 있음
    profile_link = f"https://solved.ac/profile/{username}"

    return {
        "username": username,
        "profile_image": profile_img,
        "tier_image": tier_img,
        "profile_link": profile_link
    }

# 테스트
info = get_solvedac_user_info("voyant")
print(info)
