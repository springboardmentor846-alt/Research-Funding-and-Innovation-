import { Box, Toolbar } from "@mui/material";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

function DashboardLayout({ children }) {

    return (

        <Box sx={{ display: "flex" }}>

            <Sidebar />

            <Navbar />

            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    bgcolor: "#F5F7FB",
                    minHeight: "100vh",
                    p: 4
                }}
            >

                <Toolbar />

                {children}

            </Box>

        </Box>

    );

}

export default DashboardLayout;