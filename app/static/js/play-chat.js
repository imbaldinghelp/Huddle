// The chat on the play page: sends a question to the assistant and adds the
// reply to the conversation, without reloading the page.
const chat = document.querySelector("[data-chat]");

const SEND_FAILED =
  "Huddle could not send your question. Check your connection and try again. " +
  "If you were logged out, refresh the page and log in.";

if (chat) {
  const messages = chat.querySelector("[data-chat-messages]");
  const emptyNote = chat.querySelector("[data-chat-empty]");
  const errorNote = chat.querySelector("[data-chat-error]");
  const form = chat.querySelector("[data-chat-form]");
  const input = chat.querySelector("[data-chat-input]");
  const sendButton = chat.querySelector("[data-chat-send]");
  const count = chat.querySelector("[data-chat-count]");
  const limitNote = chat.querySelector("[data-chat-limit]");

  // True from the moment a question is sent until its reply (or error) is shown.
  let waiting = false;

  // ---------- Building the conversation ----------

  function addMessage(who, text) {
    const label = document.createElement("span");
    label.className = "visually-hidden";
    label.textContent = who === "user" ? "You: " : "Assistant: ";

    const message = document.createElement("p");
    message.className = `chat-message chat-message-${who}`;
    // textContent (not innerHTML) shows the text exactly as written, so
    // nothing in a question or reply can run as code.
    message.append(label, document.createTextNode(text));
    messages.append(message);
    scrollToNewest();
    return message;
  }

  function addThinkingDots() {
    const dots = document.createElement("p");
    dots.className = "chat-message chat-thinking";
    dots.innerHTML = '<span></span><span></span><span></span><b class="visually-hidden">Thinking</b>';
    messages.append(dots);
    scrollToNewest();
    return dots;
  }

  function scrollToNewest() {
    messages.scrollTop = messages.scrollHeight;
  }

  function showError(text) {
    errorNote.textContent = text;
    errorNote.hidden = text === "";
  }

  // ---------- The question box ----------

  // The box starts one line tall and grows with the text (up to its CSS max-height).
  function fitInputToText() {
    input.style.height = "auto";
    input.style.height = `${input.scrollHeight}px`;
  }

  function showQuestionsLeft(left, limitMessage) {
    count.textContent = `${left} question${left === 1 ? "" : "s"} left today`;
    form.hidden = left <= 0;
    limitNote.hidden = left > 0;
    limitNote.textContent = limitMessage;
  }

  // ---------- Sending ----------

  async function send(question) {
    if (waiting || question === "") {
      return;
    }
    waiting = true;
    sendButton.disabled = true;
    showError("");
    emptyNote.hidden = true;
    input.value = "";
    fitInputToText();

    const ownMessage = addMessage("user", question);
    const dots = addThinkingDots();
    const result = await askServer(question);
    dots.remove();

    if (result && result.answer) {
      addMessage("assistant", result.answer);
    } else {
      // Take the question back out of the conversation and put it back in
      // the box, so it is easy to try again.
      ownMessage.remove();
      emptyNote.hidden = messages.querySelector(".chat-message") !== null;
      input.value = question;
      fitInputToText();
      showError(result && result.error ? result.error : SEND_FAILED);
    }
    if (result && typeof result.questions_left === "number") {
      showQuestionsLeft(result.questions_left, result.limit_message);
    }

    waiting = false;
    sendButton.disabled = false;
    if (!form.hidden) {
      input.focus();
    }
  }

  // The step the court is showing (1, 2, ...). play-viewer.js keeps it up to
  // date on the viewer, so "who has the ball now?" is about the right step.
  function currentStep() {
    const step = Number(document.querySelector("[data-play-viewer]")?.dataset.currentStep);
    return Number.isInteger(step) && step > 0 ? step : null;
  }

  // Returns the server's reply as an object, or null if it could not be reached.
  async function askServer(question) {
    try {
      const response = await fetch(chat.dataset.askUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": chat.dataset.csrfToken },
        body: JSON.stringify({ question, step: currentStep() }),
      });
      return await response.json();
    } catch {
      return null;
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    send(input.value.trim());
  });

  // Enter sends, like other chat apps. Shift+Enter starts a new line.
  // isComposing is true while picking a character on a Chinese/Japanese keyboard.
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  input.addEventListener("input", fitInputToText);

  // The ready-made questions shown before the first message.
  chat.querySelectorAll("[data-chat-starter]").forEach((button) => {
    button.addEventListener("click", () => send(button.textContent));
  });

  // Start at the newest message when the page opens on a long conversation.
  scrollToNewest();
}
