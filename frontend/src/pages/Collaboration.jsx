import { useEffect, useState } from "react";

import {
    Typography,
    Grid,
    Card,
    CardContent,
    Chip,
    Button,
    Avatar,
    LinearProgress
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";
import { getCollaborations } from "../services/collaborationApi";

function Collaboration() {

    const [collaborations, setCollaborations] = useState([]);

    useEffect(() => {

        loadCollaborations();

    }, []);

    async function loadCollaborations() {

        try {

            // Change this later to the logged-in user's profile id
            const result = await getCollaborations(2);

            setCollaborations(result.recommendations);

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

                Collaboration Recommendations

            </Typography>

            <Typography
                color="text.secondary"
                mb={4}
            >

                AI-powered research collaboration suggestions

            </Typography>

            <Grid container spacing={3}>

                {

                    collaborations.map((item) => (

                        <Grid
                            key={item.profile_id}
                            size={{ xs: 12, md: 6 }}
                        >

                            <Card
                                sx={{
                                    borderRadius: 3,
                                    height: "100%"
                                }}
                            >

                                <CardContent>

                                    <Avatar
                                        sx={{
                                            width: 60,
                                            height: 60,
                                            mb: 2,
                                            bgcolor: "#1976d2"
                                        }}
                                    >
                                        {item.organization.charAt(0)}
                                    </Avatar>

                                    <Typography
                                        variant="h6"
                                        fontWeight="bold"
                                    >
                                        {item.organization}
                                    </Typography>

                                    <Chip
                                        label={item.research_domain}
                                        color="primary"
                                        sx={{ mt: 1 }}
                                    />

                                    <Typography sx={{ mt: 2 }}>
                                        <b>Keywords:</b>
                                        {" "}
                                        {item.keywords}
                                    </Typography>

                                    <Typography>
                                        <b>Publications:</b>
                                        {" "}
                                        {item.publications}
                                    </Typography>

                                    <Typography>
                                        <b>Patents:</b>
                                        {" "}
                                        {item.patents}
                                    </Typography>

                                    <Typography>
                                        <b>Experience:</b>
                                        {" "}
                                        {item.experience} Years
                                    </Typography>

                                    <Typography>
                                        <b>Common Keywords:</b>
                                        {" "}
                                        {item.common_keywords}
                                    </Typography>

                                    <Typography
                                        sx={{ mt: 2 }}
                                    >
                                        Collaboration Score
                                    </Typography>

                                    <LinearProgress
                                        variant="determinate"
                                        value={Math.min(item.collaboration_score, 100)}
                                        sx={{
                                            height: 10,
                                            borderRadius: 5,
                                            mt: 1,
                                            mb: 2
                                        }}
                                    />

                                    <Typography
                                        fontWeight="bold"
                                    >
                                        {item.collaboration_score}%
                                    </Typography>

                                    <Button
                                        variant="contained"
                                        fullWidth
                                        sx={{ mt: 3 }}
                                    >
                                        Connect
                                    </Button>

                                </CardContent>

                            </Card>

                        </Grid>

                    ))

                }

            </Grid>

        </DashboardLayout>

    );

}

export default Collaboration;