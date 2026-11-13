import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";
import { API } from "../api";
import { buttonClass, inputClass } from "../styles";

export function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    const response = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        first_name: firstName,
        last_name: lastName,
        password: password,
      }),
    });
    if (!response.ok) {
      if (response.status === 409) setError("this email is already registered");
      if (response.status === 422)
        setError(
          "Check your input: Password must be at least 8 characters long, first name and last name are not empty and email must be valid",
        );
      return;
    }
    navigate("/login");
  }

  return (
    <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
      <h1 className="text-2xl font-bold">Sign up</h1>
      <input
        className={inputClass}
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        type="text"
        placeholder="First name"
      />
      <input
        className={inputClass}
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        type="text"
        placeholder="Last name"
      />
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
        Already have an account?{" "}
        <Link className="text-blue-600 underline" to="/login">
          Log in
        </Link>
      </p>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </form>
  );
}
