// 좋아요 버튼 (AJAX) - 담당: 장예희
// 페이지를 새로고침하지 않고 버튼 모양과 숫자만 바꿈
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("like-btn");
    if (!btn) return;

    btn.addEventListener("click", async function () {
        btn.disabled = true;
        try {
            const res = await fetch(btn.dataset.url, { method: "POST" });

            if (res.status === 401) {
                alert("로그인 후 좋아요를 누를 수 있어요.");
                window.location.href = btn.dataset.loginUrl;
                return;
            }
            if (!res.ok) throw new Error("request failed");

            const data = await res.json();
            btn.classList.toggle("liked", data.liked);
            btn.setAttribute("aria-pressed", data.liked ? "true" : "false");
            btn.querySelector(".like-icon").textContent = data.liked ? "♥" : "♡";
            document.getElementById("like-count").textContent = data.count;
        } catch (e) {
            alert("좋아요 처리 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요.");
        } finally {
            btn.disabled = false;
        }
    });
});
