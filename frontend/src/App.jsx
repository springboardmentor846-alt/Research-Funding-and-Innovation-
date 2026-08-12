import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import Dashboard from "./Dashboard";

function App() {
  const [token, setToken] = useState("");
  const [showRegister, setShowRegister] = useState(false);

  const handleLogout = () => {
    setToken("");
  };

  if (token) {
    return <Dashboard token={token} onLogout={handleLogout} />;
  }

  return (
    <div>
      {showRegister ? (
        <Register onSwitchToLogin={() => setShowRegister(false)} />
      ) : (
        <Login
          onLoginSuccess={(newToken) => setToken(newToken)}
          onSwitchToRegister={() => setShowRegister(true)}
        />
      )}
    </div>
  );
}

export default App;
