// Show/Hide buttons inside password fields.
// Each button toggles the input that sits in the same .field-control.
document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  const input = button.closest(".field-control").querySelector("input");

  button.addEventListener("click", () => {
    const isVisible = input.type === "text";
    input.type = isVisible ? "password" : "text";
    button.textContent = isVisible ? "Show" : "Hide";
    button.setAttribute("aria-pressed", String(!isVisible));
  });
});
