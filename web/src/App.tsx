import { useState } from "react";

const API = "http://localhost:8000";


function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
  }
  return token ? (
    <button onClick={logout}>Log out</button>
  ) : (
    <LoginForm onLogin={setToken} />
  );
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const response = await fetch(`${API}/auth/login`, {
      method: "POST",
      body: new URLSearchParams({ username: email, password: password })
    });
    if (!response.ok) {
      if (response.status === 401)
        setError("incorrect password or email");
      return;
    }
    const data = await response.json();
    const { access_token, refresh_token } = data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    onLogin(access_token);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
      <button type="submit">Submit</button>
      {error && <p>{error}</p>}
    </form>
  );
}

export default App;
