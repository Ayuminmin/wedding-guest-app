// 新郎新婦の署名（お手紙の最後に表示）。ここを書き換えてください。
const COUPLE_SIGNATURE = "Ayumi & ○○";

const inputScreen = document.getElementById("input-screen");
const messageScreen = document.getElementById("message-screen");
const form = document.getElementById("guest-form");
const nameInput = document.getElementById("name");
const passwordInput = document.getElementById("password");
const errorMessage = document.getElementById("error-message");
const letterCard = document.getElementById("letter-card");
const dearText = document.getElementById("dear-text");
const messageBody = document.getElementById("message-body");
const signatureText = document.getElementById("signature-text");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.hidden = true;

  const inputName = nameInput.value.trim();
  const inputPassword = passwordInput.value.trim().toLowerCase();

  if (!inputName || !inputPassword) {
    showError();
    return;
  }

  try {
    const guests = await loadGuests();
    const guest = guests.find((g) => {
      const guestName = String(g.name || "").trim();
      const guestPassword = String(g.password || "").trim().toLowerCase();
      return guestName === inputName && guestPassword === inputPassword;
    });

    if (guest) {
      showMessage(guest);
    } else {
      showError();
    }
  } catch (err) {
    // guests.json の読み込みに失敗した場合も、同じ柔らかいエラー表示にする
    showError();
  }
});

let cachedGuests = null;

async function loadGuests() {
  if (cachedGuests) return cachedGuests;
  const res = await fetch("guests.json");
  if (!res.ok) {
    throw new Error("guests.json の読み込みに失敗しました");
  }
  cachedGuests = await res.json();
  return cachedGuests;
}

function showError() {
  errorMessage.hidden = false;
}

function showMessage(guest) {
  dearText.textContent = `Dear ${guest.name}`;
  messageBody.textContent = guest.message;
  signatureText.textContent = COUPLE_SIGNATURE;

  inputScreen.hidden = true;
  messageScreen.hidden = false;

  // 初期状態（非表示位置）を描画させてから .show を付けて、確実にトランジションを発火させる
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      letterCard.classList.add("show");
    });
  });
}
