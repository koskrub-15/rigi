export const API = "http://localhost:8000";


export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem("access_token")
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return fetch(`${API}${path}`, { ...init, headers });
}
