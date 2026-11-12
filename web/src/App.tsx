import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { API } from "./api";
import { Header } from "./components/Header";
import { Home } from "./components/Home";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  function logout() {
    fetch(`${API}/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refresh_token: localStorage.getItem("refresh_token"),
      }),
    });
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <div className="mx-auto max-w-md p-4">
          <Routes>
            <Route
              path="/"
              element={
                token ? (
                  <>
                    <Header onLogout={logout} />
                    <Home onLogout={logout} />
                  </>
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/login"
              element={
                token ? (
                  <Navigate to="/" replace />
                ) : (
                  <LoginPage onLogin={setToken} />
                )
              }
            />
            <Route
              path="/register"
              element={token ? <Navigate to="/" replace /> : <RegisterPage />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
