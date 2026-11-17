// Assistant page. An answer can take a few seconds, so while the question is
// being sent this shows that something is happening and stops a second send.
const form = document.querySelector("[data-ask-form]");

if (form) {
  const question = form.querySelector("textarea");
  const button = form.querySelector("[data-ask-button]");
  const status = form.querySelector("[data-ask-status]");
  const idleButtonText = button.textContent;
  const idleStatusText = status.textContent;

  form.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "Thinking...";
    status.textContent = "Reading the playbook. This can take a few seconds.";
  });

  // Enter sends the question, like a chat box. Shift+Enter starts a new line.
  // isComposing is true while picking a character on a Chinese/Japanese keyboard.
  question.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  // Coming back with the browser's Back button can show the page as it was
  // left, still saying "Thinking...". Put it back to normal.
  window.addEventListener("pageshow", () => {
    button.disabled = false;
    button.textContent = idleButtonText;
    status.textContent = idleStatusText;
  });
}
