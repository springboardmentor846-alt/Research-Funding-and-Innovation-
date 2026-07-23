import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { login } = useAuth();

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await login(email, password);

      toast.success("Login successful");

      navigate("/dashboard");
    } catch (err) {
      toast.error(
        err?.response?.data?.detail || "Invalid email or password"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: 450 }}>
      <div className="card shadow">
        <div className="card-body">

          <h3 className="text-center mb-4">
            Login
          </h3>

          <form onSubmit={handleSubmit}>

            <div className="mb-3">
              <label>Email</label>

              <input
                type="email"
                className="form-control"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="mb-3">
              <label>Password</label>

              <input
                type="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              className="btn btn-primary w-100"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Login"}
            </button>

          </form>

          <div className="text-center mt-3">

            Don't have an account?

            <Link to="/register">
              {" "}Register
            </Link>

          </div>

        </div>
      </div>
    </div>
  );
}

export default Login;