
async function checkUser() {
    const username = document.querySelector(".usernameInput").value;
    const resultDiv = document.querySelector(".result");

    // fetch: JS(Front)에서 웹 API(Back)에 요청을 보내는 함수
    const getResponse = await fetch(`http://localhost:8000/submissions/${username}`);
    
    const data = await getResponse.json(); // JS 객체로 파싱

    resultDiv.innerHTML = `
    <p><strong>User:</strong> ${data.user}</p>
    <img src="${data.profileImg}" width="100" alt="프로필"><br>
    <p><strong>오늘 푼 문제 수:</strong> ${data.problems.length}개</p>
    <p>${data.problems.length > 0 ? "오늘 문제 풀었어!" : "얼른 문제 푸세요!"}</p>
    <p><strong>문제 목록:</strong> ${data.problems.join(", ")}</p>
    `;
}
