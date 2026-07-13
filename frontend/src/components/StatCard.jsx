import { Card, CardContent, Typography } from "@mui/material";

function StatCard({

    title,

    value,

    color

}) {

    return (

        <Card
            sx={{
                minWidth: 240,
                borderRadius: 3,
                boxShadow: 4,
                borderLeft: `6px solid ${color}`
            }}
        >

            <CardContent>

                <Typography
                    variant="subtitle1"
                    color="text.secondary"
                >

                    {title}

                </Typography>

                <Typography
                    variant="h4"
                    fontWeight="bold"
                    sx={{ mt: 2 }}
                >

                    {value}

                </Typography>

            </CardContent>

        </Card>

    );

}

export default StatCard;