// 자동 실행 제거
window.onload = () => {
    const saved = localStorage.getItem("usernames");
    if (saved) {
        document.querySelector(".usernameInput").value = saved;
        // checkUsers(saved); 자동 실행 제거
    }
};

function loadSaved() {
    const saved = localStorage.getItem("usernames");
    if (!saved) {
        alert("저장된 계정이 없습니다");
        return;
    }
    document.querySelector(".usernameInput").value = saved;
    checkUsers(saved);
}

const profileCache = {}; // user profileImg 저장

async function checkUsers(inputText = null) {
    const input = inputText || document.querySelector(".usernameInput").value;
    const usernames = input.split(",").map(u => u.trim()).filter(u => u);
    const container = document.querySelector(".result-container");

    if (usernames.length === 0 || usernames.length > 10) {
        alert("1명 이상, 최대 10명까지 입력해주세요!");
        return;
    }

    localStorage.setItem("usernames", input);

    // 기존 카드 유지하고, 텍스트만 업데이트
    for (const username of usernames) {
        let card = document.getElementById(`user-card-${username}`);

        try {
            const res = await fetch(`http://localhost:8000/submissions/${username}`);
            const data = await res.json();

            // 이미지 캐싱
            if (!profileCache[username]) {
                profileCache[username] = data.profileImg;
            }

            const problemList = data.problems.join(", ");
            const solved = data.problems.length > 0;

            const cardHTML = `
                <p><strong>${data.user}</strong></p>
                <p>오늘 푼 문제 수: ${data.problems.length}개</p>
                <p style="color: ${solved ? 'green' : 'red'};">
                    ${solved ? "오늘 문제 풀었어!" : "얼른 문제 푸세요!"}
                </p>
                <p>${problemList}</p>
            `;

            // 카드 없으면 새로 생성
            if (!card) {
                card = document.createElement("div");
                card.className = "user-card";
                card.id = `user-card-${username}`;
                card.innerHTML = `<img src="${profileCache[username]}" alt="프로필 이미지" />` + cardHTML;
                container.appendChild(card);
            } else {
                // 기존 카드 내용만 업데이트
                card.innerHTML = `<img src="${profileCache[username]}" alt="프로필 이미지" />` + cardHTML;
            }

        } catch (err) {
            if (!card) {
                const errorCard = document.createElement("div");
                errorCard.className = "user-card";
                errorCard.id = `user-card-${username}`;
                errorCard.innerHTML = `
                    <p><strong>${username}</strong></p>
                    <p style="color: red;">정보를 불러오지 못했어요.</p>
                `;
                container.appendChild(errorCard);
            }
        }
    }
}


async function checkProblem() {
    const problemId = document.querySelector(".problemInput").value.trim();
    const saved = localStorage.getItem("usernames");
    const resultDiv = document.querySelector(".problem-result");

    if (!saved || !problemId) {
        alert("계정과 문제 번호를 입력해주세요!");
        return;
    }

    const users = saved;
    resultDiv.innerHTML = "";

    try {
        const res = await fetch(`http://localhost:8000/problem_check/${problemId}?users=${users}`);
        const data = await res.json();

        // 제목 카드
        const title = document.createElement("div");
        title.innerHTML = `<h3>문제 ${data.problem}번</h3>`;
        title.style.width = "100%";
        title.style.textAlign = "center";
        resultDiv.appendChild(title);

        for (const item of data.results) {
            const card = document.createElement("div");
            card.className = "problem-card";
            const emoji = item.solved ? "✅" : "❌";
            const msg = item.solved ? "풀었음" : "안 풀었음";
            const reaction = item.solved
                ? `<p style="color: green;">멋져요!!</p>`
                : `<p style="color: red;">얼른 문제 푸세요!</p>`;

            card.innerHTML = `
                <p><strong>${item.user}</strong></p>
                <p style="font-size: 20px;">${emoji} ${msg}</p>
                ${reaction}
            `;
            resultDiv.appendChild(card);
        }


    } catch (err) {
        resultDiv.innerHTML = "<p style='color:red;'>오류 발생: " + err.message + "</p>";
    }
}


function clearSaved() {
    localStorage.removeItem("usernames");
    document.querySelector(".usernameInput").value = "";
    document.querySelector(".result-container").innerHTML = "";
}