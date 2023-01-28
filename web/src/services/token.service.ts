const TOKEN_KEY = "truba_token";

export const tokenService = {
  removeToken,
  setToken,
  getToken,
};

function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function setToken(token: string): void {
  if (!token) {
    return;
  }
  localStorage.removeItem(TOKEN_KEY);
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
