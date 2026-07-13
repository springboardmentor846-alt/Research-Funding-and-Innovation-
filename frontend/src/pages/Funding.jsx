import { useEffect, useState } from "react";

import {
    Typography,
    Paper,
    Grid,
    TextField,
    Button,
    Card,
    CardContent,
    Chip
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";

import {
    getRecommendations,
    searchFunding
} from "../services/fundingApi";

function Funding() {

    const [fundings, setFundings] = useState([]);

    const [domain, setDomain] = useState(
        "Artificial Intelligence"
    );

    useEffect(() => {

        loadRecommendations();

    }, []);

    async function loadRecommendations() {

        try {

            const result = await getRecommendations();

            setFundings(
                result["Recommended Funding"]
            );

        }

        catch (error) {

            console.log(error);

        }

    }

    async function handleSearch() {

        try {

            const result = await searchFunding(domain);

            setFundings(result);

        }

        catch (error) {

            console.log(error);

        }

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={1}
            >

                Funding Discovery

            </Typography>

            <Typography
                color="text.secondary"
                mb={4}
            >

                Search and explore research funding opportunities

            </Typography>

            <Paper
                sx={{
                    p: 3,
                    mb: 4,
                    borderRadius: 3
                }}
            >

                <Grid
                    container
                    spacing={2}
                >

                    <Grid size={{ xs: 12, md: 9 }}>

                        <TextField

                            fullWidth

                            label="Research Domain"

                            value={domain}

                            onChange={(e) =>
                                setDomain(
                                    e.target.value
                                )
                            }

                        />

                    </Grid>

                    <Grid size={{ xs: 12, md: 3 }}>

                        <Button

                            fullWidth

                            variant="contained"

                            sx={{ height: "56px" }}

                            onClick={handleSearch}

                        >

                            Search

                        </Button>

                    </Grid>

                </Grid>

            </Paper>

            <Grid
                container
                spacing={3}
            >

                {

                    fundings.map((item) => (

                        <Grid
                            key={item.id}
                            size={{ xs: 12, md: 6 }}
                        >

                            <Card
                                sx={{
                                    borderRadius: 3,
                                    height: "100%"
                                }}
                            >

                                <CardContent>

                                    <Typography
                                        variant="h6"
                                        fontWeight="bold"
                                    >

                                        {item.title}

                                    </Typography>

                                    <Typography>

                                        <b>Agency:</b> {item.funding_agency}

                                    </Typography>

                                    <Typography>

                                        <b>Amount:</b>

                                        ₹{item.funding_amount.toLocaleString()}

                                    </Typography>

                                    <Typography>

                                        <b>Eligibility:</b>

                                        {item.eligibility}

                                    </Typography>

                                    <Typography>

                                        <b>Deadline:</b>

                                        {item.deadline}

                                    </Typography>

                                    <Typography
                                        sx={{
                                            mt: 2
                                        }}
                                    >

                                        {item.description}

                                    </Typography>

                                    <Chip

                                        label={
                                            item.research_domain
                                        }

                                        color="primary"

                                        sx={{
                                            mt: 2
                                        }}

                                    />

                                </CardContent>

                            </Card>

                        </Grid>

                    ))

                }

            </Grid>

        </DashboardLayout>

    );

}

export default Funding;