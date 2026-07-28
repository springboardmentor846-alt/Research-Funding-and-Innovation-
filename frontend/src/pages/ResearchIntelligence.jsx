import { useEffect, useState } from "react";
import { Grid, Paper, Typography, Table, TableHead, TableBody, TableRow, TableCell } from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";
import StatCard from "../components/StatCard";
import ResearchImpactChart from "../components/ResearchImpactChart";
import TechnologyReadinessChart from "../components/TechnologyReadinessChart";

import {
    getDashboard,
    getResearchImpact,
    getTechnologyReadiness,
    getCommercialViability,
    getFundingAttractiveness
} from "../services/researchIntelligenceApi";

function ResearchIntelligence() {
    const [dashboard, setDashboard] = useState({});
    const [researchImpact, setResearchImpact] = useState([]);
    const [technology, setTechnology] = useState([]);
    const [commercial, setCommercial] = useState([]);
    const [funding, setFunding] = useState([]);

    async function loadData() {
        try {
            setDashboard(await getDashboard());
            setResearchImpact(await getResearchImpact());
            setTechnology(await getTechnologyReadiness());
            setCommercial(await getCommercialViability());
            setFunding(await getFundingAttractiveness());
        } catch (err) {
            console.log(err);
        }
    }

    useEffect(() => {
        loadData();
    }, []);

    return (
        <DashboardLayout>
            <Typography variant="h4" fontWeight="bold" mb={4}>
                Research Intelligence Dashboard
            </Typography>

            <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                    <StatCard title="Assessments" value={dashboard["Total Assessments"]} />
                </Grid>

                <Grid item xs={12} md={3}>
                    <StatCard title="Average Score" value={dashboard["Average Innovation Score"]} />
                </Grid>

                <Grid item xs={12} md={3}>
                    <StatCard title="Highest Score" value={dashboard["Highest Innovation Score"]} />
                </Grid>

                <Grid item xs={12} md={3}>
                    <StatCard title="Top Researcher" value={dashboard["Top Researcher"]} />
                </Grid>
            </Grid>

            <Grid container spacing={3} mt={2}>
                <Grid item xs={12} md={7}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" mb={2}>
                            Research Impact
                        </Typography>
                        <ResearchImpactChart data={researchImpact} />
                    </Paper>
                </Grid>

                <Grid item xs={12} md={5}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" mb={2}>
                            Technology Readiness
                        </Typography>
                        <TechnologyReadinessChart data={technology} />
                    </Paper>
                </Grid>
            </Grid>

            <Grid container spacing={3} mt={2}>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" mb={2}>
                            Commercial Viability
                        </Typography>

                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Researcher</TableCell>
                                    <TableCell>Market</TableCell>
                                    <TableCell>Status</TableCell>
                                </TableRow>
                            </TableHead>

                            <TableBody>
                                {commercial.map((item, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{item.Researcher}</TableCell>
                                        <TableCell>{item["Market Potential"]}</TableCell>
                                        <TableCell>{item["Commercial Viability"]}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" mb={2}>
                            Funding Attractiveness
                        </Typography>

                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Researcher</TableCell>
                                    <TableCell>Funding</TableCell>
                                    <TableCell>Recommendation</TableCell>
                                </TableRow>
                            </TableHead>

                            <TableBody>
                                {funding.map((item, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{item.Researcher}</TableCell>
                                        <TableCell>{item["Funding Relevance"]}</TableCell>
                                        <TableCell>{item["Funding Attractiveness"]}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                </Grid>
            </Grid>
        </DashboardLayout>
    );
}

export default ResearchIntelligence;