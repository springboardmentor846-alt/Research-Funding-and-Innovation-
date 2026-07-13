import { useEffect, useState } from "react";

import {
    Typography,
    Grid,
    Paper,
    Chip,
    CircularProgress
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";

import { getProfile } from "../services/profileApi";

import StatCard from "../components/StatCard";

function ResearchProfile() {

    const [profile, setProfile] = useState(null);

    useEffect(() => {

        async function loadProfile() {

            try {

                const result = await getProfile();

                setProfile(result.data);

            }

            catch (error) {

                console.log(error);

            }

        }

        loadProfile();

    }, []);

    if (!profile) {

        return (

            <DashboardLayout>

                <CircularProgress />

            </DashboardLayout>

        );

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={1}
            >

                Research Profile

            </Typography>

            <Typography
                color="text.secondary"
                mb={4}
            >

                Researcher Information & Academic Profile

            </Typography>

            <Paper
                elevation={3}
                sx={{
                    p: 4,
                    borderRadius: 3,
                    mb: 4
                }}
            >

                <Typography variant="h5">

                    Organization

                </Typography>

                <Typography mb={2}>

                    {profile.organization}

                </Typography>

                <Typography variant="h5">

                    Research Domain

                </Typography>

                <Typography mb={2}>

                    {profile.research_domain}

                </Typography>

                <Typography variant="h5">

                    Keywords

                </Typography>

                <div
                    style={{
                        marginTop: "10px"
                    }}
                >

                    {

                        profile.keywords

                        .split(",")

                        .map((item, index) => (

                            <Chip

                                key={index}

                                label={item.trim()}

                                sx={{
                                    mr: 1,
                                    mb: 1
                                }}

                            />

                        ))

                    }

                </div>

            </Paper>

            <Grid
                container
                spacing={3}
            >

                <Grid size={{ xs: 12, md: 4 }}>

                    <StatCard

                        title="Publications"

                        value={profile.publications}

                        color="#2563EB"

                    />

                </Grid>

                <Grid size={{ xs: 12, md: 4 }}>

                    <StatCard

                        title="Patents"

                        value={profile.patents}

                        color="#16A34A"

                    />

                </Grid>

                <Grid size={{ xs: 12, md: 4 }}>

                    <StatCard

                        title="Experience"

                        value={profile.experience + " Years"}

                        color="#EA580C"

                    />

                </Grid>

            </Grid>

        </DashboardLayout>

    );

}

export default ResearchProfile;