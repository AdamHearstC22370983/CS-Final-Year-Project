const TOKEN_KEY = "skillgap_access_token";
const USER_KEY = "skillgap_current_user";

// Store the current authenticated session from the backend login response.
export function setAuthSession(payload) {
  if (!payload?.access_token || !payload?.user) {
    throw new Error("Invalid auth payload.");
  }

  localStorage.setItem(TOKEN_KEY, payload.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
}

// Return the stored JWT access token.
export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

// Return the stored current user object.
export function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    clearCurrentUser();
    return null;
  }
}

// Update only the stored user object without touching the token.
export function setCurrentUser(user) {
  if (!user) {
    localStorage.removeItem(USER_KEY);
    return;
  }

  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// True only when both token and user are present.
export function isLoggedIn() {
  return Boolean(getAccessToken() && getCurrentUser());
}

// Clear the whole auth session.
export function clearCurrentUser() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}