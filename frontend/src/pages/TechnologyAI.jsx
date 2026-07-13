import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";

import {
    Typography,
    Grid,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    LinearProgress
} from "@mui/material";

import PublicationChart from "../components/PublicationChart";
import CitationChart from "../components/CitationChart";
import TRLChart from "../components/TRLChart";

import {
    getTechnologyDashboard,
    getForecast,
    getOrganizationRanking,
    getResearchProductivity,
    getCollaborationNetwork
} from "../services/technologyApi";

function TechnologyAI() {

    const [dashboard, setDashboard] = useState(null);
    const [forecast, setForecast] = useState([]);
    const [organizations, setOrganizations] = useState([]);
    const [productivity, setProductivity] = useState([]);
    const [network, setNetwork] = useState([]);

    useEffect(() => {

        loadData();

    }, []);

    async function loadData() {

        try {

            const dash = await getTechnologyDashboard();

            const trend = await getForecast();

            const org = await getOrganizationRanking();

            const prod = await getResearchProductivity();

            const net = await getCollaborationNetwork();

            setDashboard(dash);

            setForecast(trend.forecast);

            setOrganizations(org.organizations);

            setProductivity(prod.productivity);

            setNetwork(net.network);

        }

        catch (error) {

            console.log(error);

        }

    }

    if (!dashboard) {

        return (

            <DashboardLayout>

                <Typography variant="h5">

                    Loading Technology Intelligence...

                </Typography>

            </DashboardLayout>

        );

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={4}
            >

                Technology Intelligence Dashboard

            </Typography>

            <Grid container spacing={3}>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography>Total Papers</Typography>
                            <Typography variant="h4">
                                {dashboard.overview.total_papers}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography>Total Citations</Typography>
                            <Typography variant="h4">
                                {dashboard.overview.total_citations}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography>Total Funding</Typography>
                            <Typography variant="h4">
                                {dashboard.overview.total_funding}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography>Average TRL</Typography>
                            <Typography variant="h4">
                                {dashboard.overview.average_trl}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

            </Grid>

            <br />

            <PublicationChart
                data={dashboard.publication_chart}
            />

            <br />

            <CitationChart
                data={dashboard.citation_chart}
            />

            <br />

            <TRLChart
                data={dashboard.trl_chart}
            />

            <br />

            <Typography
                variant="h5"
                fontWeight="bold"
                mb={2}
            >

                Forecast Trends

            </Typography>

            <Grid container spacing={3}>

                {

                    forecast.map((item, index) => (

                        <Grid item xs={12} md={6} key={index}>

                            <Card>

                                <CardContent>

                                    <Typography variant="h6">

                                        {item.research_domain}

                                    </Typography>

                                    <Chip
                                        label={item.prediction}
                                        color="success"
                                        sx={{ mt: 1 }}
                                    />

                                    <Typography sx={{ mt: 2 }}>

                                        Papers : {item.papers}

                                    </Typography>

                                    <Typography>

                                        Avg Citations : {item.average_citations}

                                    </Typography>

                                    <Typography>

                                        Avg TRL : {item.average_trl}

                                    </Typography>

                                    <Typography>

                                        Trend Score

                                    </Typography>

                                    <LinearProgress
                                        variant="determinate"
                                        value={Math.min(item.trend_score / 15,100)}
                                        sx={{ mt: 1 }}
                                    />

                                </CardContent>

                            </Card>

                        </Grid>

                    ))

                }

            </Grid>

            <br />

            <Typography variant="h5" fontWeight="bold">

                Organization Ranking

            </Typography>

            <TableContainer
                component={Paper}
                sx={{ mt:2 }}
            >

                <Table>

                    <TableHead>

                        <TableRow>

                            <TableCell>Organization</TableCell>

                            <TableCell>Researchers</TableCell>

                            <TableCell>Publications</TableCell>

                            <TableCell>Patents</TableCell>

                            <TableCell>Citations</TableCell>

                            <TableCell>Score</TableCell>

                        </TableRow>

                    </TableHead>

                    <TableBody>

                        {

                            organizations.map((item,index)=>(

                                <TableRow key={index}>

                                    <TableCell>{item.organization}</TableCell>

                                    <TableCell>{item.researchers}</TableCell>

                                    <TableCell>{item.publications}</TableCell>

                                    <TableCell>{item.patents}</TableCell>

                                    <TableCell>{item.citations}</TableCell>

                                    <TableCell>{item.organization_score}</TableCell>

                                </TableRow>

                            ))

                        }

                    </TableBody>

                </Table>

            </TableContainer>

            <br />

            <Typography variant="h5" fontWeight="bold">

                Research Productivity

            </Typography>

            <TableContainer component={Paper} sx={{ mt:2 }}>

                <Table>

                    <TableHead>

                        <TableRow>

                            <TableCell>Organization</TableCell>

                            <TableCell>Publications</TableCell>

                            <TableCell>Patents</TableCell>

                            <TableCell>Experience</TableCell>

                            <TableCell>Productivity</TableCell>

                            <TableCell>Score</TableCell>

                        </TableRow>

                    </TableHead>

                    <TableBody>

                        {

                            productivity.map((item,index)=>(

                                <TableRow key={index}>

                                    <TableCell>{item.organization}</TableCell>

                                    <TableCell>{item.publications}</TableCell>

                                    <TableCell>{item.patents}</TableCell>

                                    <TableCell>{item.experience}</TableCell>

                                    <TableCell>{item.productivity}</TableCell>

                                    <TableCell>{item.productivity_score}</TableCell>

                                </TableRow>

                            ))

                        }

                    </TableBody>

                </Table>

            </TableContainer>

            <br />

            <Typography variant="h5" fontWeight="bold">

                Collaboration Network

            </Typography>

            <TableContainer component={Paper} sx={{ mt:2 }}>

                <Table>

                    <TableHead>

                        <TableRow>

                            <TableCell>Researcher 1</TableCell>

                            <TableCell>Researcher 2</TableCell>

                            <TableCell>Domain</TableCell>

                            <TableCell>Common Keywords</TableCell>

                            <TableCell>Score</TableCell>

                        </TableRow>

                    </TableHead>

                    <TableBody>

                        {

                            network.map((item,index)=>(

                                <TableRow key={index}>

                                    <TableCell>{item.researcher_1}</TableCell>

                                    <TableCell>{item.researcher_2}</TableCell>

                                    <TableCell>{item.domain}</TableCell>

                                    <TableCell>{item.common_keywords.join(", ")}</TableCell>

                                    <TableCell>{item.collaboration_score}</TableCell>

                                </TableRow>

                            ))

                        }

                    </TableBody>

                </Table>

            </TableContainer>

        </DashboardLayout>

    );

}

export default TechnologyAI;