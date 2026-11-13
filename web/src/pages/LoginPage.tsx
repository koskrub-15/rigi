import { useState, type FormEvent } from "react";
import { Link } from "react-router";
import { API } from "../api";
import { buttonClass, inputClass } from "../styles";

export function LoginPage({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    const response = await fetch(`${API}/auth/login`, {
      method: "POST",
      body: new URLSearchParams({ username: email, password: password }),
    });
    if (!response.ok) {
      if (response.status === 401) setError("incorrect password or email");
      return;
    }
    const data = await response.json();
    const { access_token, refresh_token } = data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    onLogin(access_token);
  }

  return (
    <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
      <h1 className="text-2xl font-bold">Log in</h1>
      <input
        className={inputClass}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        type="email"
        placeholder="Email"
      />
      <input
        className={inputClass}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="Password"
      />
      <button className={buttonClass} type="submit">
        Submit
      </button>
      <p>
        Don't have an account?{" "}
        <Link className="text-blue-600 underline" to="/register">
          Register
        </Link>
      </p>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </form>
  );
}
