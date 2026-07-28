import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Grid,
  Paper,
  Container,
} from "@mui/material";
import {
  Science,
  AccountBalance,
  Insights,
  Groups,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";

function Landing() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#0F172A,#1E3A8A,#2563EB)",
        color: "white",
      }}
    >
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: "transparent",
          boxShadow: "none",
        }}
      >
        <Toolbar>
          <Typography
            variant="h5"
            sx={{
              flexGrow: 1,
              fontWeight: "bold",
            }}
          >
            Research Funding Platform
          </Typography>

          <Button
            variant="contained"
            color="secondary"
            onClick={() => navigate("/login")}
          >
            Login
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        <Box
          sx={{
            textAlign: "center",
            mt: 10,
            mb: 8,
          }}
        >
          <Typography
            variant="h2"
            fontWeight="bold"
          >
            Research Funding Platform
          </Typography>

          <Typography
            variant="h5"
            sx={{
              mt: 3,
              color: "#E5E7EB",
            }}
          >
            AI Powered Innovation Intelligence
          </Typography>

          <Typography
            sx={{
              mt: 3,
              fontSize: 18,
              color: "#D1D5DB",
            }}
          >
            Empowering Researchers, Startups,
            Innovation Managers and Administrators
            through Funding Discovery,
            Patent Analytics,
            Technology Intelligence,
            Commercialization and Collaboration.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          <Grid item xs={12} md={3}>
            <Paper
              sx={{
                p: 4,
                textAlign: "center",
                borderRadius: 3,
              }}
            >
              <Science
                color="primary"
                sx={{ fontSize: 55 }}
              />

              <Typography
                variant="h6"
                mt={2}
              >
                Research
              </Typography>

              <Typography color="text.secondary">
                Manage researcher profiles and publications.
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper
              sx={{
                p: 4,
                textAlign: "center",
                borderRadius: 3,
              }}
            >
              <AccountBalance
                color="primary"
                sx={{ fontSize: 55 }}
              />

              <Typography
                variant="h6"
                mt={2}
              >
                Funding
              </Typography>

              <Typography color="text.secondary">
                Discover grants and funding opportunities.
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper
              sx={{
                p: 4,
                textAlign: "center",
                borderRadius: 3,
              }}
            >
              <Insights
                color="primary"
                sx={{ fontSize: 55 }}
              />

              <Typography
                variant="h6"
                mt={2}
              >
                Innovation
              </Typography>

              <Typography color="text.secondary">
                AI-powered technology intelligence and patent analytics.
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={3}>
            <Paper
              sx={{
                p: 4,
                textAlign: "center",
                borderRadius: 3,
              }}
            >
              <Groups
                color="primary"
                sx={{ fontSize: 55 }}
              />

              <Typography
                variant="h6"
                mt={2}
              >
                Collaboration
              </Typography>

              <Typography color="text.secondary">
                Connect researchers, startups and industry.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default Landing;