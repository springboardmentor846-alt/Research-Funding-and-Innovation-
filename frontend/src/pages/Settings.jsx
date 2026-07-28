import { useEffect, useState } from "react";
import {
    Box,
    Grid,
    Typography,
    Card,
    CardContent,
    Avatar,
    TextField,
    Button,
    Divider,
    Alert
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";

import {
    getProfile,
    updateProfile,
    changePassword,
    getDashboardStats
} from "../services/settingsApi";

function Settings() {

    const [profile, setProfile] = useState({});

    const [stats, setStats] = useState({});

    const [passwords, setPasswords] = useState({
        old_password: "",
        new_password: "",
        confirm_password: ""
    });

    const [message, setMessage] = useState("");

    useEffect(() => {

        loadData();

    }, []);

    async function loadData() {

        try {

            const profileData = await getProfile();

            const dashboard = await getDashboardStats();

            setProfile(profileData.user || profileData);

            setStats(dashboard.overview);

        }

        catch (err) {

            console.log(err);

        }

    }

    async function saveProfile() {

        try {

            await updateProfile(profile);

            setMessage("Profile Updated Successfully");

        }

        catch {

            setMessage("Failed to update profile");

        }

    }

    async function updatePassword() {

        if (
            passwords.new_password !==
            passwords.confirm_password
        ) {

            alert("Passwords do not match");

            return;

        }

        try {

            await changePassword(passwords);

            alert("Password Updated");

            setPasswords({
                old_password: "",
                new_password: "",
                confirm_password: ""
            });

        }

        catch {

            alert("Password Update Failed");

        }

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={4}
            >
                My Account
            </Typography>

            {message &&

                <Alert sx={{ mb:3 }}>

                    {message}

                </Alert>

            }

            <Grid container spacing={3}>

                {/* Profile */}

                <Grid item xs={12} md={8}>

                    <Card>

                        <CardContent>

                            <Box
                                display="flex"
                                alignItems="center"
                                gap={3}
                                mb={3}
                            >

                                <Avatar
                                    sx={{
                                        width:80,
                                        height:80,
                                        bgcolor:"#1565C0",
                                        fontSize:32
                                    }}
                                >
                                    {profile.full_name?.charAt(0)}
                                </Avatar>

                                <Box>

                                    <Typography variant="h5">

                                        {profile.full_name}

                                    </Typography>

                                    <Typography color="text.secondary">

                                        {profile.role}

                                    </Typography>

                                </Box>

                            </Box>

                            <Divider sx={{ mb:3 }}/>

                            <Grid container spacing={2}>

                                <Grid item xs={12} md={6}>

                                    <TextField
                                        fullWidth
                                        label="Full Name"
                                        value={profile.full_name || ""}
                                        onChange={(e)=>

                                            setProfile({
                                                ...profile,
                                                full_name:e.target.value
                                            })

                                        }
                                    />

                                </Grid>

                                <Grid item xs={12} md={6}>

                                    <TextField
                                        disabled
                                        fullWidth
                                        label="Email"
                                        value={profile.email || ""}
                                    />

                                </Grid>

                                <Grid item xs={12} md={6}>

                                    <TextField
                                        fullWidth
                                        label="Organization"
                                        value={profile.organization || ""}
                                        onChange={(e)=>

                                            setProfile({
                                                ...profile,
                                                organization:e.target.value
                                            })

                                        }
                                    />

                                </Grid>

                                <Grid item xs={12} md={6}>

                                    <TextField
                                        disabled
                                        fullWidth
                                        label="Role"
                                        value={profile.role || ""}
                                    />

                                </Grid>

                            </Grid>

                            <Button
                                sx={{ mt:3 }}
                                variant="contained"
                                onClick={saveProfile}
                            >

                                Save Changes

                            </Button>

                        </CardContent>

                    </Card>

                </Grid>

                {/* Statistics */}

                <Grid item xs={12} md={4}>

                    <Card>

                        <CardContent>

                            <Typography
                                variant="h6"
                                gutterBottom
                            >
                                My Statistics
                            </Typography>

                            <Typography>

                                Research Papers :
                                {stats?.total_papers ?? 0}

                            </Typography>

                            <Typography>

                                Funding :
                                {stats?.total_funding ?? 0}

                            </Typography>

                            <Typography>

                                Citations :
                                {stats?.total_citations ?? 0}

                            </Typography>

                            <Typography>

                                Average TRL :
                                {stats?.average_trl ?? 0}

                            </Typography>

                        </CardContent>

                    </Card>

                </Grid>

                {/* Password */}

                <Grid item xs={12}>

                    <Card>

                        <CardContent>

                            <Typography
                                variant="h6"
                                gutterBottom
                            >
                                Change Password
                            </Typography>

                            <Grid container spacing={2}>

                                <Grid item xs={12} md={4}>

                                    <TextField
                                        fullWidth
                                        type="password"
                                        label="Current Password"
                                        value={passwords.old_password}
                                        onChange={(e)=>

                                            setPasswords({

                                                ...passwords,

                                                old_password:e.target.value

                                            })

                                        }
                                    />

                                </Grid>

                                <Grid item xs={12} md={4}>

                                    <TextField
                                        fullWidth
                                        type="password"
                                        label="New Password"
                                        value={passwords.new_password}
                                        onChange={(e)=>

                                            setPasswords({

                                                ...passwords,

                                                new_password:e.target.value

                                            })

                                        }
                                    />

                                </Grid>

                                <Grid item xs={12} md={4}>

                                    <TextField
                                        fullWidth
                                        type="password"
                                        label="Confirm Password"
                                        value={passwords.confirm_password}
                                        onChange={(e)=>

                                            setPasswords({

                                                ...passwords,

                                                confirm_password:e.target.value

                                            })

                                        }
                                    />

                                </Grid>

                            </Grid>

                            <Button
                                variant="contained"
                                sx={{ mt:3 }}
                                onClick={updatePassword}
                            >

                                Update Password

                            </Button>

                        </CardContent>

                    </Card>

                </Grid>

            </Grid>

        </DashboardLayout>

    );

}

export default Settings;