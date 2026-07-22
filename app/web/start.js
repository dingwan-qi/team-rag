/**
 * 课程资料智能问答系统开始界面
 * 登录 / 注册 / 首页动效
 */

const petalsContainer = document.getElementById("petals");
const MAX_PETALS = 30;
let petalCount = 0;

function createPetal() {
    if (petalCount >= MAX_PETALS) return;

    const petal = document.createElement("div");
    petal.classList.add("petal");

    const size = 10 + Math.random() * 16;
    const startX = window.innerWidth * (0.4 + Math.random() * 0.6);
    const startY = -40 - Math.random() * 80;
    const duration = 9 + Math.random() * 12;
    const delay = Math.random() * 5;
    const colors = [
        "radial-gradient(ellipse at 35% 35%, rgba(255,220,200,0.95) 0%, rgba(255,185,160,0.7) 50%, rgba(255,170,145,0) 100%)",
        "radial-gradient(ellipse at 35% 35%, rgba(255,235,220,0.9) 0%, rgba(255,210,185,0.6) 50%, rgba(255,200,175,0) 100%)",
        "radial-gradient(ellipse at 35% 35%, rgba(255,200,180,0.9) 0%, rgba(255,160,140,0.65) 50%, rgba(255,145,125,0) 100%)",
    ];

    petal.style.cssText = `
        left: ${startX}px;
        top: ${startY}px;
        width: ${size}px;
        height: ${size}px;
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        animation-duration: ${duration}s;
        animation-delay: ${delay}s;
    `;

    petalsContainer.appendChild(petal);
    petalCount++;

    setTimeout(() => {
        if (petal.parentNode) {
            petal.remove();
            petalCount--;
        }
    }, (duration + delay) * 1000);
}

function seedPetals(count) {
    for (let i = 0; i < count; i++) {
        setTimeout(() => createPetal(), i * 180);
    }
}

setInterval(() => {
    if (petalCount < MAX_PETALS) createPetal();
}, 700);

seedPetals(18);

const subtitleLines = document.querySelectorAll(".subtitle-line");
const TYPE_SPEED = 60;
const LINE_PAUSE = 400;

function typeLine(el, text, onDone) {
    el.classList.add("visible");
    el.textContent = "";

    const cursor = document.createElement("span");
    cursor.classList.add("cursor");
    el.appendChild(cursor);

    let i = 0;
    const timer = setInterval(() => {
        if (i < text.length) {
            el.insertBefore(document.createTextNode(text[i]), cursor);
            i++;
            return;
        }
        clearInterval(timer);
        cursor.remove();
        if (onDone) setTimeout(onDone, LINE_PAUSE);
    }, TYPE_SPEED + Math.random() * 30);
}

function startTypewriter() {
    const texts = Array.from(subtitleLines).map((el) => el.textContent.trim());
    subtitleLines.forEach((el) => {
        el.textContent = "";
    });

    let idx = 0;
    function next() {
        if (idx < subtitleLines.length) {
            typeLine(subtitleLines[idx], texts[idx], () => {
                idx++;
                next();
            });
        }
    }
    next();
}

setTimeout(startTypewriter, 600);

const ctaButton = document.getElementById("ctaButton");
if (ctaButton) {
    ctaButton.addEventListener("mousemove", (event) => {
        const rect = ctaButton.getBoundingClientRect();
        ctaButton.style.setProperty("--btn-x", `${event.clientX - rect.left}px`);
        ctaButton.style.setProperty("--btn-y", `${event.clientY - rect.top}px`);
    });

    ctaButton.addEventListener("mouseleave", () => {
        ctaButton.style.setProperty("--btn-x", "50%");
        ctaButton.style.setProperty("--btn-y", "50%");
    });
}

const ctaSection = document.getElementById("ctaSection");
const loginCard = document.getElementById("loginCard");
const backBtn = document.getElementById("backBtn");
let isLoginVisible = false;

ctaButton.addEventListener("click", () => {
    if (isLoginVisible) return;
    isLoginVisible = true;
    ctaSection.classList.add("fading");
    setTimeout(() => loginCard.classList.add("visible"), 300);
});

backBtn.addEventListener("click", () => {
    if (!isLoginVisible) return;
    loginCard.classList.remove("visible");
    setTimeout(() => {
        ctaSection.classList.remove("fading");
        isLoginVisible = false;
        showLoginMode();
        setMessage("");
    }, 300);
});

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const authMessage = document.getElementById("authMessage");
const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");
const forgotPwd = document.getElementById("forgotPwd");

showRegister.addEventListener("click", (event) => {
    event.preventDefault();
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    setMessage("");
});

showLogin.addEventListener("click", (event) => {
    event.preventDefault();
    showLoginMode();
});

forgotPwd.addEventListener("click", (event) => {
    event.preventDefault();
    setMessage("演示系统暂未接入密码找回，请联系组长重置账号。");
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;
    await submitAuth("/api/auth/login", { username, password }, loginForm, "登录中...");
});

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("registerUsername").value.trim();
    const password = document.getElementById("registerPassword").value;
    const confirm = document.getElementById("registerConfirm").value;
    if (password !== confirm) {
        setMessage("两次输入的密码不一致", "error");
        shakeElement(registerForm.querySelector(".login-btn"));
        return;
    }
    await submitAuth("/api/auth/register", { username, password }, registerForm, "注册中...");
});

async function submitAuth(path, payload, form, loadingText) {
    if (!payload.username || !payload.password) {
        setMessage("请输入账号和密码", "error");
        shakeElement(form.querySelector(".login-btn"));
        return;
    }

    const button = form.querySelector(".login-btn");
    const original = button.innerHTML;
    button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
    button.disabled = true;
    setMessage("");

    try {
        const response = await fetch(path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "请求失败");
        }
        localStorage.setItem("teamrag_token", data.token);
        localStorage.setItem("teamrag_user", JSON.stringify(data.user));
        setMessage("登录成功，正在进入问答系统...", "success");
        button.innerHTML = '<i class="fas fa-check"></i> 登录成功';
        button.style.background = "linear-gradient(135deg, #7d9a6b 0%, #5d7a4b 100%)";
        setTimeout(() => {
            window.location.href = "qa-index.html";
        }, 600);
    } catch (error) {
        setMessage(error.message || "登录失败", "error");
        shakeElement(button);
        button.innerHTML = original;
        button.disabled = false;
    }
}

function showLoginMode() {
    registerForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
    setMessage("");
}

function setMessage(message, type = "") {
    authMessage.textContent = message;
    authMessage.className = `auth-message ${type}`.trim();
}

function shakeElement(el) {
    el.style.animation = "none";
    el.offsetHeight;
    el.style.animation = "shake 0.5s ease";
    setTimeout(() => {
        el.style.animation = "";
    }, 500);
}

const shakeStyle = document.createElement("style");
shakeStyle.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-6px); }
        40% { transform: translateX(6px); }
        60% { transform: translateX(-4px); }
        80% { transform: translateX(4px); }
    }
`;
document.head.appendChild(shakeStyle);

document.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && isLoginVisible) {
        const activeEl = document.activeElement;
        if (activeEl && activeEl.closest(".login-card")) {
            const form = registerForm.classList.contains("hidden") ? loginForm : registerForm;
            form.dispatchEvent(new Event("submit", { cancelable: true }));
        }
    }
});

let resizeDebounce;
window.addEventListener("resize", () => {
    clearTimeout(resizeDebounce);
    resizeDebounce = setTimeout(() => {
        const petals = petalsContainer.querySelectorAll(".petal");
        petals.forEach((petal) => {
            const rect = petal.getBoundingClientRect();
            if (rect.left > window.innerWidth || rect.top < -80) {
                petal.remove();
                petalCount--;
            }
        });
    }, 300);
});
