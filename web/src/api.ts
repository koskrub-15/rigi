let tokenPromise: Promise<boolean> | null = null;

export const API = "http://localhost:8000";


export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const response = await fetch(`${API}${path}`, {
    ...init, headers: getHeaders(init.headers)
  });
  if (response.status === 401) {
    if (await refreshTokens()) {
      return fetch(`${API}${path}`, {
        ...init, headers: getHeaders(init.headers)
      });
    }
    return response;
  }
  return response;
}

function getHeaders(initHeaders: HeadersInit | undefined): Headers {
  const token = localStorage.getItem("access_token");
  const headers = new Headers(initHeaders);
  headers.set("Authorization", `Bearer ${token}`);
  return headers;
}


async function refreshTokens(): Promise<boolean> {
  if (tokenPromise === null) {
    tokenPromise = fetchTokens();
  }
  const result = await tokenPromise;
  tokenPromise = null;
  return result;
}


async function fetchTokens(): Promise<boolean> {
  if (localStorage.getItem("refresh_token") === null) {
    return false;
  }
  const response = await fetch(`${API}/auth/refresh`, { headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: localStorage.getItem("refresh_token") }), method: "POST" });
  if (response.ok) {
    const data = await response.json();
    const { access_token, refresh_token } = data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    return true;
  }
  return false;
}
