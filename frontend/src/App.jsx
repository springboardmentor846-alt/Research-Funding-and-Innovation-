import { useState } from "react";
import axios from "axios";
import "./App.css";
import Dashboard from "./Dashboard";

function App() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loggedIn, setLoggedIn] = useState(
  localStorage.getItem("token") ? true : false
);
  const handleLogin = async () => {

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/login",
        {
          email: email,
          password: password
        }
      );

      localStorage.setItem("token", response.data.access_token);

      alert("Login Successful");
      setLoggedIn(true);

      console.log(response.data);

    } catch (error) {

      alert("Invalid Email or Password");

      console.log(error);

    }

  };

  if (loggedIn) {
  return <Dashboard setLoggedIn={setLoggedIn} />;
}
  return (
    <div className="container">
      <div className="login-box">

        <h1>Research Funding</h1>

<p>Innovation Intelligence Platform</p>

        <input
          type="email"
          placeholder="Enter Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Enter Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleLogin}>
          Login
        </button>

      </div>
    </div>
  );
}

export default App;