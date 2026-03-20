//theme.js
const THEME_KEY = "skillgap_theme";
//function returns the current theme in use by the system
export function getCurrentTheme() {
  return localStorage.getItem(THEME_KEY) || "light";
}
//function to apply the alternate dark mode theme
export function applyTheme(theme) {
  const finalTheme = theme === "dark" ? "dark" : "light";

  localStorage.setItem(THEME_KEY, finalTheme);
  document.body.setAttribute("data-theme", finalTheme);

  window.dispatchEvent(
    new CustomEvent("skillgap-theme-change", {
      detail: finalTheme,
    })
  );
}
//function used to turn on and off dark mode
export function toggleTheme() {
  const current = getCurrentTheme();
  const next = current === "dark" ? "light" : "dark";
  applyTheme(next);
  return next;
}