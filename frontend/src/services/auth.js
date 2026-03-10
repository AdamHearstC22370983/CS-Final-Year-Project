const STORAGE_KEY = "skillgap_user";

export function saveCurrentUser(user) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function getCurrentUser() {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearCurrentUser() {
  localStorage.removeItem(STORAGE_KEY);
}

export function isLoggedIn() {
  return !!getCurrentUser();
}