import { useEffect, useState } from "react";

import {
    Typography,
    Grid,
    Box,
    Paper
} from "@mui/material";

import { useNavigate } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";

import { getDashboard } from "../services/dashboardApi";

import StatCard from "../components/StatCard";

import PublicationChart from "../components/PublicationChart";
import CitationChart from "../components/CitationChart";
import DomainChart from "../components/DomainChart";
import FundingChart from "../components/FundingChart";
import TRLChart from "../components/TRLChart";

function Dashboard() {

    const [data, setData] = useState(null);

    const navigate = useNavigate();

    useEffect(() => {

        async function loadDashboard() {

            try {

                const result = await getDashboard();

                setData(result);

            }

            catch (error) {

                console.error(error);

            }

        }

        loadDashboard();

    }, []);

    if (!data) {

        return (

            <DashboardLayout>

                <Typography variant="h5">

                    Loading Dashboard...

                </Typography>

            </DashboardLayout>

        );

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                gutterBottom
            >

                Research Funding Platform Dashboard

            </Typography>

            <Typography
                color="text.secondary"
                sx={{ mb: 4 }}
            >

                AI Powered Research & Innovation Intelligence

            </Typography>

            <Grid
                container
                spacing={3}
            >

                <Grid size={{ xs: 12, md: 3 }}>

                    <StatCard
                        title="Research Papers"
                        value={data.overview.total_papers}
                        color="#2563EB"
                    />

                </Grid>

                <Grid size={{ xs: 12, md: 3 }}>

                    <StatCard
                        title="Total Citations"
                        value={data.overview.total_citations}
                        color="#16A34A"
                    />

                </Grid>

                <Grid size={{ xs: 12, md: 3 }}>

                    <StatCard
                        title="Average TRL"
                        value={data.overview.average_trl}
                        color="#7C3AED"
                    />

                </Grid>

                <Grid size={{ xs: 12, md: 3 }}>

                    <StatCard
                        title="Funding Opportunities"
                        value={data.overview.total_funding}
                        color="#dbea0c"
                    />

                </Grid>

            </Grid>

            {/* NEW QUICK ACCESS SECTION */}

            <Grid
                container
                spacing={3}
                mt={3}
            >

                <Grid size={{ xs: 12, md: 4 }}>

                    <Paper
                        elevation={4}
                        sx={{
                            p: 3,
                            cursor: "pointer",
                            borderRadius: 3,
                            transition: "0.3s",
                            "&:hover": {
                                transform: "translateY(-5px)",
                                boxShadow: 8
                            }
                        }}
                        onClick={() => navigate("/research-intelligence")}
                    >

                        <Typography
                            variant="h6"
                            fontWeight="bold"
                        >

                            Research Intelligence

                        </Typography>

                        <Typography
                            mt={1}
                            color="text.secondary"
                        >

                            View Research Impact, Technology Readiness,
                            Commercial Viability and Funding
                            Attractiveness Analytics.

                        </Typography>

                    </Paper>

                </Grid>

            </Grid>

            <Box mt={5}>

                <PublicationChart
                    data={data.publication_chart}
                />

            </Box>

            <Box mt={5}>

                <CitationChart
                    data={data.citation_chart}
                />

            </Box>

            <Box mt={5}>

                <DomainChart
                    data={data.domain_chart}
                />

            </Box>

            <Box mt={5}>

                <FundingChart
                    data={data.funding_chart}
                />

            </Box>

            <Box mt={5}>

                <TRLChart
                    data={data.trl_chart}
                />

            </Box>

        </DashboardLayout>

    );

}

export default Dashboard;