import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import { login } from "../services/authApi";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    try {
      const data = await login(email, password);

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("email", email);

      navigate("/dashboard");
    } catch (err) {
      alert("Invalid Email or Password");
    }
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#0F172A,#1E3A8A,#2563EB)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Paper
        elevation={10}
        sx={{
          width: 420,
          p: 5,
          borderRadius: 4,
        }}
      >
        <Typography
          variant="h4"
          align="center"
          fontWeight="bold"
          mb={1}
        >
          Login
        </Typography>

        <Typography
          align="center"
          color="text.secondary"
          mb={4}
        >
          Welcome to Research Funding Platform
        </Typography>

        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Email"
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextField
            fullWidth
            type="password"
            label="Password"
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button
            fullWidth
            variant="contained"
            size="large"
            type="submit"
            sx={{ mt: 3 }}
          >
            Login
          </Button>
        </form>

        <Typography
          align="center"
          mt={3}
        >
          New User?{" "}
          <Link
            component="button"
            underline="hover"
            onClick={() => navigate("/register")}
          >
            Register Here
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}

export default Login;