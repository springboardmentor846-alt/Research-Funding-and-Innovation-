import { Paper, Typography } from "@mui/material";

function ChartCard({ title, children }) {

    return (

        <Paper
            elevation={3}
            sx={{
                p: 3,
                borderRadius: 3,
                height: "100%"
            }}
        >

            <Typography
                variant="h6"
                fontWeight="bold"
                mb={2}
            >
                {title}
            </Typography>

            {children}

        </Paper>

    );

}

export default ChartCard;