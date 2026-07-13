import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  MenuItem,
  Link,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    organization: "",
    role: "Researcher",
  });

  const roles = [
    "Researcher",
    "Startup Founder",
    "Innovation Manager",
    "Administrator",
  ];

  async function handleRegister(e) {
    e.preventDefault();

    try {
      await axios.post("http://127.0.0.1:8000/register", form);

      alert("Registration Successful");

      navigate("/login");
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Registration Failed"
      );
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
          width: 500,
          p: 5,
          borderRadius: 4,
        }}
      >
        <Typography
          variant="h4"
          align="center"
          fontWeight="bold"
        >
          Create Account
        </Typography>

        <Typography
          align="center"
          color="text.secondary"
          mb={4}
        >
          Research Funding Platform
        </Typography>

        <form onSubmit={handleRegister}>
          <TextField
            fullWidth
            margin="normal"
            label="Full Name"
            value={form.full_name}
            onChange={(e) =>
              setForm({
                ...form,
                full_name: e.target.value,
              })
            }
          />

          <TextField
            fullWidth
            margin="normal"
            label="Email"
            value={form.email}
            onChange={(e) =>
              setForm({
                ...form,
                email: e.target.value,
              })
            }
          />

          <TextField
            fullWidth
            type="password"
            margin="normal"
            label="Password"
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
          />

          <TextField
            fullWidth
            margin="normal"
            label="Organization"
            value={form.organization}
            onChange={(e) =>
              setForm({
                ...form,
                organization: e.target.value,
              })
            }
          />

          <TextField
            select
            fullWidth
            margin="normal"
            label="Role"
            value={form.role}
            onChange={(e) =>
              setForm({
                ...form,
                role: e.target.value,
              })
            }
          >
            {roles.map((role) => (
              <MenuItem key={role} value={role}>
                {role}
              </MenuItem>
            ))}
          </TextField>

          <Button
            fullWidth
            variant="contained"
            size="large"
            sx={{ mt: 3 }}
            type="submit"
          >
            Register
          </Button>
        </form>

        <Typography
          align="center"
          mt={3}
        >
          Already have an account?{" "}
          <Link
            component="button"
            underline="hover"
            onClick={() => navigate("/login")}
          >
            Login
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}

export default Register;