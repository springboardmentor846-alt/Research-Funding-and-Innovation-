import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Grid,
  Stack,
  Avatar,
  Chip,
} from "@mui/material";

import ScienceIcon from "@mui/icons-material/Science";
import PsychologyIcon from "@mui/icons-material/Psychology";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import GroupsIcon from "@mui/icons-material/Groups";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";

import { useNavigate } from "react-router-dom";

function Landing() {

    const navigate = useNavigate();

    return (

<Box
sx={{
minHeight:"100vh",
overflow:"hidden",
position:"relative",
background:
"linear-gradient(135deg,#07152F,#0E2A59,#173D8F,#325ED9)"
}}
>

{/* Animated Background */}

<Box
sx={{
position:"absolute",
width:650,
height:650,
borderRadius:"50%",
background:"rgba(82,146,255,.18)",
filter:"blur(90px)",
top:-220,
left:-180,
animation:"floatOne 8s infinite ease-in-out",
"@keyframes floatOne":{
"0%":{transform:"translateY(0px)"},
"50%":{transform:"translateY(40px)"},
"100%":{transform:"translateY(0px)"}
}
}}
/>

<Box
sx={{
position:"absolute",
width:420,
height:420,
borderRadius:"50%",
background:"rgba(255,255,255,.08)",
filter:"blur(80px)",
right:-100,
bottom:-100,
animation:"floatTwo 10s infinite ease-in-out",
"@keyframes floatTwo":{
"0%":{transform:"translateY(0px)"},
"50%":{transform:"translateY(-40px)"},
"100%":{transform:"translateY(0px)"}
}
}}
/>

{/* NAVBAR */}

<AppBar

position="static"

sx={{

background:"transparent",

boxShadow:"none",

padding:2

}}

>

<Toolbar>

<Typography

variant="h5"

fontWeight="bold"

sx={{

flexGrow:1,

color:"white"

}}

>

Research Funding Platform

</Typography>

<Stack

direction="row"

spacing={4}

mr={5}

>

<Button sx={{color:"white"}}>

Home

</Button>

<Button sx={{color:"white"}}>

Features

</Button>

<Button sx={{color:"white"}}>

Research

</Button>

<Button sx={{color:"white"}}>

Contact

</Button>

</Stack>

<Button

variant="contained"

size="large"

sx={{

borderRadius:8,

px:4,

background:"#7C3AED"

}}

onClick={()=>navigate("/login")}

>

Login

</Button>

</Toolbar>

</AppBar>

{/* HERO */}

<Grid

container

spacing={6}

alignItems="center"

sx={{

height:"85vh",

px:8,

position:"relative",

zIndex:2

}}

>

{/* LEFT */}

<Grid item xs={12} md={6}>

<Chip

icon={<AutoAwesomeIcon/>}

label="AI Powered Innovation"

sx={{

mb:4,

background:"rgba(255,255,255,.15)",

color:"white",

backdropFilter:"blur(20px)"

}}

/>

<Typography

variant="h2"

fontWeight="bold"

color="white"

>

Accelerating

<br/>

Research Innovation

</Typography>

<Typography

mt={4}

fontSize={22}

color="rgba(255,255,255,.85)"

lineHeight={2}

>

Discover research funding opportunities,

analyze patents,

collaborate with innovators,

track commercialization,

and receive AI-powered recommendations

through one intelligent platform.

</Typography>

<Stack

direction="row"

spacing={3}

mt={6}

>

<Button

variant="contained"

size="large"

endIcon={<ArrowForwardIcon/>}

sx={{

px:5,

py:1.5,

borderRadius:4,

fontSize:18,

background:"#7C3AED"

}}

onClick={()=>navigate("/login")}

>

Get Started

</Button>

<Button

variant="outlined"

size="large"

sx={{

color:"white",

borderColor:"white",

borderRadius:4,

px:5

}}

>

Explore Platform

</Button>

</Stack>

<Stack

direction="row"

spacing={6}

mt={7}

>

<Box>

<Typography

variant="h3"

fontWeight="bold"

color="white"

>

1200+

</Typography>

<Typography color="#E3F2FD">

Researchers

</Typography>

</Box>

<Box>

<Typography

variant="h3"

fontWeight="bold"

color="white"

>

350+

</Typography>

<Typography color="#E3F2FD">

Funding Calls

</Typography>

</Box>

<Box>

<Typography

variant="h3"

fontWeight="bold"

color="white"

>

98%

</Typography>

<Typography color="#E3F2FD">

Success Rate

</Typography>

</Box>

</Stack>

</Grid>
{/* RIGHT */}

<Grid item xs={12} md={6}>

<Box
sx={{
position:"relative",
height:650
}}
>

{/* Main Dashboard */}

<Box
sx={{
position:"absolute",
right:30,
top:20,
width:470,
height:560,
borderRadius:"35px",
background:"rgba(255,255,255,.12)",
backdropFilter:"blur(30px)",
border:"1px solid rgba(255,255,255,.25)",
boxShadow:"0 25px 60px rgba(0,0,0,.25)",
p:4,
animation:"dashboardFloat 6s ease-in-out infinite",
"@keyframes dashboardFloat":{
"0%":{transform:"translateY(0px)"},
"50%":{transform:"translateY(-15px)"},
"100%":{transform:"translateY(0px)"}
}
}}
>

<Typography
variant="h5"
fontWeight="bold"
color="white"
mb={4}
>
Research Analytics
</Typography>

<Box
sx={{
display:"flex",
justifyContent:"space-between",
mb:4
}}
>

<Box>

<Typography
color="#90CAF9"
variant="body2"
>
Funding Score
</Typography>

<Typography
variant="h4"
fontWeight="bold"
color="white"
>
92%
</Typography>

</Box>

<TrendingUpIcon
sx={{
fontSize:55,
color:"#4ADE80"
}}
/>

</Box>

<Box
sx={{
height:12,
background:"rgba(255,255,255,.15)",
borderRadius:20,
overflow:"hidden",
mb:5
}}
>

<Box
sx={{
width:"92%",
height:"100%",
background:"linear-gradient(90deg,#00E5FF,#3B82F6)"
}}
/>

</Box>

<Stack spacing={3}>

<Box
sx={{
display:"flex",
justifyContent:"space-between",
alignItems:"center"
}}
>

<Box
display="flex"
alignItems="center"
gap={2}
>

<ScienceIcon sx={{color:"#90CAF9"}}/>

<Box>

<Typography color="white">
Patent Intelligence
</Typography>

<Typography color="#BFD8FF" fontSize={14}>
128 Patents
</Typography>

</Box>

</Box>

<Chip
label="98%"
color="success"
/>

</Box>

<Box
sx={{
display:"flex",
justifyContent:"space-between",
alignItems:"center"
}}
>

<Box
display="flex"
alignItems="center"
gap={2}
>

<AccountBalanceIcon sx={{color:"#FFD54F"}}/>

<Box>

<Typography color="white">
Funding Discovery
</Typography>

<Typography color="#BFD8FF" fontSize={14}>
356 Active Grants
</Typography>

</Box>

</Box>

<Chip
label="Live"
color="primary"
/>

</Box>

<Box
sx={{
display:"flex",
justifyContent:"space-between",
alignItems:"center"
}}
>

<Box
display="flex"
alignItems="center"
gap={2}
>

<PsychologyIcon sx={{color:"#F472B6"}}/>

<Box>

<Typography color="white">
AI Recommendation
</Typography>

<Typography color="#BFD8FF" fontSize={14}>
Personalized Results
</Typography>

</Box>

</Box>

<Chip
label="AI"
color="secondary"
/>

</Box>

<Box
sx={{
display:"flex",
justifyContent:"space-between",
alignItems:"center"
}}
>

<Box
display="flex"
alignItems="center"
gap={2}
>

<GroupsIcon sx={{color:"#22D3EE"}}/>

<Box>

<Typography color="white">
Research Collaboration
</Typography>

<Typography color="#BFD8FF" fontSize={14}>
74 Active Teams
</Typography>

</Box>

</Box>

<Chip
label="Active"
color="info"
/>

</Box>

</Stack>

</Box>

{/* Floating Card 1 */}

<Box
sx={{
position:"absolute",
top:70,
left:0,
width:220,
borderRadius:"25px",
background:"rgba(255,255,255,.15)",
backdropFilter:"blur(25px)",
p:3,
animation:"cardOne 5s infinite ease-in-out",
"@keyframes cardOne":{
"0%":{transform:"translateY(0px)"},
"50%":{transform:"translateY(-15px)"},
"100%":{transform:"translateY(0px)"}
}
}}
>

<NotificationsActiveIcon
sx={{
color:"#FFD54F",
fontSize:40
}}
/>

<Typography
mt={2}
fontWeight="bold"
color="white"
>

New Grant Alert

</Typography>

<Typography
fontSize={14}
color="#E3F2FD"
>

15 new AI research grants available.

</Typography>

</Box>

{/* Floating Card 2 */}

<Box
sx={{
position:"absolute",
bottom:60,
left:40,
width:240,
borderRadius:"25px",
background:"rgba(255,255,255,.15)",
backdropFilter:"blur(25px)",
p:3,
animation:"cardTwo 6s infinite ease-in-out",
"@keyframes cardTwo":{
"0%":{transform:"translateY(0px)"},
"50%":{transform:"translateY(12px)"},
"100%":{transform:"translateY(0px)"}
}
}}
>

<Stack
direction="row"
spacing={2}
alignItems="center"
>

<Avatar
sx={{
bgcolor:"#7C3AED"
}}
>

AI

</Avatar>

<Box>

<Typography
fontWeight="bold"
color="white"
>

Innovation Score

</Typography>

<Typography
color="#E3F2FD"
fontSize={14}
>

Excellent • 94%

</Typography>

</Box>

</Stack>

</Box>

</Box>

</Grid>

</Grid>
{/* ================= FEATURES SECTION ================= */}

<Box
    sx={{
        py: 10,
        px: 8,
        position: "relative",
        zIndex: 2
    }}
>

    <Typography
        variant="h3"
        align="center"
        color="white"
        fontWeight="bold"
        mb={2}
    >
        Platform Features
    </Typography>

    <Typography
        align="center"
        color="#D6E4FF"
        mb={7}
        fontSize={20}
    >
        Everything you need to accelerate research and innovation.
    </Typography>

    <Grid container spacing={4}>

        {[
            {
                title:"Funding Discovery",
                icon:"💰",
                desc:"Discover government, industry and international funding opportunities."
            },

            {
                title:"Patent Intelligence",
                icon:"📄",
                desc:"Analyze patents, trends and technology domains."
            },

            {
                title:"Technology Analytics",
                icon:"🤖",
                desc:"AI driven technology recommendations and innovation insights."
            },

            {
                title:"Commercialization",
                icon:"🚀",
                desc:"Assess commercialization opportunities and startup potential."
            },

            {
                title:"Research Collaboration",
                icon:"🤝",
                desc:"Collaborate with researchers, universities and industries."
            },

            {
                title:"Innovation Dashboard",
                icon:"📊",
                desc:"Visual dashboards for funding, patents and innovation scoring."
            }

        ].map((item,index)=>(

            <Grid item xs={12} md={4} key={index}>

                <Box

                    sx={{

                        p:4,

                        borderRadius:"28px",

                        backdropFilter:"blur(25px)",

                        background:"rgba(255,255,255,.10)",

                        border:"1px solid rgba(255,255,255,.18)",

                        color:"white",

                        transition:".4s",

                        height:260,

                        "&:hover":{

                            transform:"translateY(-12px)",

                            background:"rgba(255,255,255,.16)",

                            boxShadow:"0 25px 60px rgba(0,0,0,.25)"

                        }

                    }}

                >

                    <Typography
                        fontSize={52}
                    >

                        {item.icon}

                    </Typography>

                    <Typography

                        mt={3}

                        variant="h5"

                        fontWeight="bold"

                    >

                        {item.title}

                    </Typography>

                    <Typography

                        mt={2}

                        color="#D8E4FF"

                    >

                        {item.desc}

                    </Typography>

                </Box>

            </Grid>

        ))}

    </Grid>

</Box>

{/* ================= FOOTER ================= */}

<Box

sx={{

py:5,

textAlign:"center",

color:"#D6E4FF",

background:"rgba(0,0,0,.15)",

backdropFilter:"blur(20px)"

}}

>

<Typography variant="h5" fontWeight="bold">

Research Funding Platform

</Typography>

<Typography mt={2}>

AI Powered Innovation Intelligence Platform

</Typography>

<Typography mt={2}>

© 2026 Research Funding Platform. All Rights Reserved.

</Typography>

</Box>

</Box>

);

}

export default Landing;