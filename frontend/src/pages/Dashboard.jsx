import { useEffect, useState } from "react";

import { Typography, Grid, Box } from "@mui/material";

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