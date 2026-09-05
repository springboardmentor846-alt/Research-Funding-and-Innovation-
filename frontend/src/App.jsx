import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import Dashboard from "./Dashboard";
import ForgotPassword from "./ForgotPassword";
import ResetPassword from "./ResetPassword";

// If the URL has a ?token= param, the user arrived from a password-reset
// email link, so open the Reset Password view directly.
const hasResetToken = new URLSearchParams(window.location.search).has("token");

function App() {
  const [token, setToken] = useState("");
  const [authView, setAuthView] = useState(
    hasResetToken ? "reset-password" : "login"
  );

  const handleLogout = () => {
    setToken("");
    setAuthView("login");
  };

  if (token) {
    return <Dashboard token={token} onLogout={handleLogout} />;
  }

  if (authView === "register") {
    return <Register onSwitchToLogin={() => setAuthView("login")} />;
  }

  if (authView === "forgot-password") {
    return <ForgotPassword onSwitchToLogin={() => setAuthView("login")} />;
  }

  if (authView === "reset-password") {
    return <ResetPassword onSwitchToLogin={() => setAuthView("login")} />;
  }

  return (
    <div>
      <Login
        onLoginSuccess={(newToken) => setToken(newToken)}
        onSwitchToRegister={() => setAuthView("register")}
        onSwitchToForgotPassword={() => setAuthView("forgot-password")}
      />
    </div>
  );
}

export default App;