import {
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
    Box
} from "@mui/material";

import {
    Link,
    useNavigate
} from "react-router-dom";

import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PersonIcon from "@mui/icons-material/Person";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import SchoolIcon from "@mui/icons-material/School";
import DescriptionIcon from "@mui/icons-material/Description";
import GroupsIcon from "@mui/icons-material/Groups";
import MemoryIcon from "@mui/icons-material/Memory";
import BusinessIcon from "@mui/icons-material/Business";
import AssessmentIcon from "@mui/icons-material/Assessment";
import SettingsIcon from "@mui/icons-material/Settings";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import LogoutIcon from "@mui/icons-material/Logout";

const drawerWidth = 260;

const menuItems = [

    {
        text: "Dashboard",
        icon: <DashboardIcon />,
        path: "/dashboard"
    },

    {
        text: "Research Profile",
        icon: <PersonIcon />,
        path: "/research-profile"
    },

    {
        text: "Funding Discovery",
        icon: <AccountTreeIcon />,
        path: "/funding"
    },

    {
        text: "Research Intelligence",
        icon: <SchoolIcon />,
        path: "/technology-ai"
    },

    {
        text: "Patent Analytics",
        icon: <DescriptionIcon />,
        path: "/papers"
    },

    {
        text: "Collaboration",
        icon: <GroupsIcon />,
        path: "/collaboration"
    },

    {
        text: "Technology Intelligence",
        icon: <MemoryIcon />,
        path: "/technology-ai"
    },

    {
    text: "Commercialization",
    icon: <RocketLaunchIcon />,
    path: "/commercialization"
},
{
    text: "Innovation",
    icon: <AutoAwesomeIcon />,
    path: "/innovation"
},
    {
        text: "Organization Ranking",
        icon: <BusinessIcon />,
        path: "/organization"
    },

    {
        text: "Reports",
        icon: <AssessmentIcon />,
        path: "/reports"
    },

    {
        text: "Settings",
        icon: <SettingsIcon />,
        path: "/settings"
    }

];

function Sidebar() {

    const navigate = useNavigate();

    const handleLogout = () => {

        localStorage.removeItem("token");

        localStorage.removeItem("email");

        navigate("/login");

    };

    return (

        <Drawer
            variant="permanent"
            sx={{
                width: drawerWidth,
                flexShrink: 0,

                "& .MuiDrawer-paper": {

                    width: drawerWidth,

                    boxSizing: "border-box",

                    background: "#13294B",

                    color: "white"

                }

            }}
        >

            <Toolbar>

                <Box>

                    <Typography
                        variant="h6"
                        fontWeight="bold"
                    >

                        RFI Platform

                    </Typography>

                    <Typography
                        variant="caption"
                    >

                        Innovation Intelligence

                    </Typography>

                </Box>

            </Toolbar>

            <List>

                {

                    menuItems.map((item) => (

                        <ListItemButton
                            key={item.text}
                            component={Link}
                            to={item.path}
                        >

                            <ListItemIcon
                                sx={{ color: "white" }}
                            >

                                {item.icon}

                            </ListItemIcon>

                            <ListItemText
                                primary={item.text}
                            />

                        </ListItemButton>

                    ))

                }

            </List>

            <Box sx={{ flexGrow: 1 }} />

            <List>

                <ListItemButton
                    onClick={handleLogout}
                >

                    <ListItemIcon
                        sx={{ color: "white" }}
                    >

                        <LogoutIcon />

                    </ListItemIcon>

                    <ListItemText
                        primary="Logout"
                    />

                </ListItemButton>

            </List>

        </Drawer>

    );

}

export default Sidebar;