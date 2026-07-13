import { Grid, Card, CardContent, Typography } from "@mui/material";

function PatentAnalytics({ analytics }) {

    if (!analytics) return null;

    return (

        <Grid container spacing={3} sx={{ mb: 4 }}>

            <Grid item xs={12} md={3}>

                <Card
                    sx={{
                        borderRadius: 3,
                        boxShadow: 3
                    }}
                >
                    <CardContent>

                        <Typography color="text.secondary">
                            Total Patents
                        </Typography>

                        <Typography
                            variant="h4"
                            fontWeight="bold"
                        >
                            {analytics["Total Patents"]}
                        </Typography>

                    </CardContent>
                </Card>

            </Grid>

            <Grid item xs={12} md={3}>

                <Card
                    sx={{
                        borderRadius: 3,
                        boxShadow: 3
                    }}
                >
                    <CardContent>

                        <Typography color="text.secondary">
                            Total Citations
                        </Typography>

                        <Typography
                            variant="h4"
                            fontWeight="bold"
                        >
                            {analytics["Total Citations"]}
                        </Typography>

                    </CardContent>
                </Card>

            </Grid>

            <Grid item xs={12} md={3}>

                <Card
                    sx={{
                        borderRadius: 3,
                        boxShadow: 3
                    }}
                >
                    <CardContent>

                        <Typography color="text.secondary">
                            Average Citations
                        </Typography>

                        <Typography
                            variant="h4"
                            fontWeight="bold"
                        >
                            {analytics["Average Citations"]}
                        </Typography>

                    </CardContent>
                </Card>

            </Grid>

            <Grid item xs={12} md={3}>

                <Card
                    sx={{
                        borderRadius: 3,
                        boxShadow: 3
                    }}
                >
                    <CardContent>

                        <Typography color="text.secondary">
                            Top Patent
                        </Typography>

                        <Typography
                            fontWeight="bold"
                        >
                            {analytics["Top Patent"]?.title}
                        </Typography>

                    </CardContent>
                </Card>

            </Grid>

        </Grid>

    );

}

export default PatentAnalytics;