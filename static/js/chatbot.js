const chatWindow = document.getElementById("chat-window");
const chatInput = document.getElementById("chat-text");
const chatSend = document.getElementById("chat-send");

function appendMessage(sender, text) {
  const div = document.createElement("div");
  div.style.marginBottom = "8px";
  div.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;
  appendMessage("You", text);
  chatInput.value = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json();
    appendMessage("Bot", data.reply || "No reply from server");
  } catch (err) {
    appendMessage("Bot", "⚠️ Error connecting to server.");
  }
}

chatSend?.addEventListener("click", sendMessage);
chatInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// const chatWindow = document.getElementById("chat-window");
// const chatInput = document.getElementById("chat-text");
// const chatSend = document.getElementById("chat-send");

// function appendMessage(sender, text) {
//   const div = document.createElement("div");
//   div.style.marginBottom = "8px";
//   div.innerHTML = `<strong>${sender}:</strong> ${text}`;
//   chatWindow.appendChild(div);
//   chatWindow.scrollTop = chatWindow.scrollHeight;
// }

// function botReply(q) {
//   const normalized = q.toLowerCase();
//   if (normalized.includes("diabetes")) {
//     return "For diabetes risk, consider fasting glucose, BMI, and age.";
//   }
//   if (normalized.includes("heart")) {
//     return "Heart risk often relates to blood pressure, cholesterol, and exercise.";
//   }
//   if (normalized.includes("parkinson")) {
//     return "Parkinson's indicators can involve voice measures and motor symptoms.";
//   }
//   return "Try asking about diabetes, heart disease, or Parkinson's.";
// }

// chatSend?.addEventListener("click", () => {
//   const text = chatInput.value.trim();
//   if (!text) return;
//   appendMessage("You", text);
//   chatInput.value = "";
//   setTimeout(() => appendMessage("Bot", botReply(text)), 300);
// });

// chatInput?.addEventListener("keydown", (e) => {
//   if (e.key === "Enter") {
//     chatSend.click();
//   }
// });
