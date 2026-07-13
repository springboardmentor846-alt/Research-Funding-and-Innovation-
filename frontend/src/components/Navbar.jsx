import {
    AppBar,
    Toolbar,
    Typography,
    Box,
    IconButton,
    Avatar,
    Badge,
    TextField,
    InputAdornment
} from "@mui/material";

import NotificationsIcon from "@mui/icons-material/Notifications";
import SearchIcon from "@mui/icons-material/Search";

function Navbar() {

    const email = localStorage.getItem("email") || "User";

    const role = localStorage.getItem("role") || "User";

    const avatarLetter = email.charAt(0).toUpperCase();

    return (

        <AppBar
            position="fixed"
            elevation={0}
            sx={{
                width: "calc(100% - 260px)",
                ml: "260px",
                background: "#ffffff",
                color: "#1F2937",
                borderBottom: "1px solid #E5E7EB"
            }}
        >

            <Toolbar>

                <Typography
                    variant="h5"
                    fontWeight="bold"
                    sx={{ flexGrow: 1 }}
                >
                    Research Funding & Innovation Intelligence Platform
                </Typography>

                <TextField
                    size="small"
                    placeholder="Search..."
                    sx={{
                        width: 260,
                        mr: 3,
                        background: "#F8FAFC",
                        borderRadius: 2
                    }}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        )
                    }}
                />

                <IconButton>

                    <Badge
                        badgeContent={4}
                        color="error"
                    >

                        <NotificationsIcon />

                    </Badge>

                </IconButton>

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        ml: 3
                    }}
                >

                    <Avatar
                        sx={{
                            bgcolor: "#2563EB",
                            mr: 2
                        }}
                    >
                        {avatarLetter}
                    </Avatar>

                    <Box>

                        <Typography fontWeight="bold">

                            {email}

                        </Typography>

                        <Typography
                            variant="caption"
                            color="text.secondary"
                        >

                            {role}

                        </Typography>

                    </Box>

                </Box>

            </Toolbar>

        </AppBar>

    );

}

export default Navbar;