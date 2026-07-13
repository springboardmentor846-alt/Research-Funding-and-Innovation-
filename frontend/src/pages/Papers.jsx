import { useEffect, useState } from "react";

import {
    Typography,
    Grid,
    Card,
    CardContent,
    Chip,
    TextField,
    InputAdornment
} from "@mui/material";

import SearchIcon from "@mui/icons-material/Search";
import DashboardLayout from "../layouts/DashboardLayout";
import { getPapers } from "../services/paperApi";

function Papers() {

    const [papers, setPapers] = useState([]);

    const [search, setSearch] = useState("");

    useEffect(() => {

        loadPapers();

    }, []);

    async function loadPapers() {

        try {

            const result = await getPapers();

            setPapers(result.data);

        }

        catch (error) {

            console.log(error);

        }

    }

    const filteredPapers = papers.filter((paper) =>

        paper.title
            .toLowerCase()
            .includes(search.toLowerCase())

    );

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={1}
            >

                Research Papers

            </Typography>

            <Typography
                color="text.secondary"
                mb={4}
            >

                Browse research publications and citation analytics

            </Typography>

            <TextField

                fullWidth

                placeholder="Search Research Papers..."

                value={search}

                onChange={(e) =>
                    setSearch(e.target.value)
                }

                sx={{ mb: 4 }}

                InputProps={{

                    startAdornment: (

                        <InputAdornment position="start">

                            <SearchIcon />

                        </InputAdornment>

                    )

                }}

            />

            <Grid
                container
                spacing={3}
            >

                {

                    filteredPapers.map((paper) => (

                        <Grid
                            key={paper.id}
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
                                        gutterBottom
                                    >

                                        {paper.title}

                                    </Typography>

                                    <Chip

                                        label={paper.domain}

                                        color="primary"

                                        sx={{ mb: 2 }}

                                    />

                                    <Typography>

                                        <b>Citations :</b>

                                        {" "}

                                        {paper.citations.toLocaleString()}

                                    </Typography>

                                </CardContent>

                            </Card>

                        </Grid>

                    ))

                }

            </Grid>

        </DashboardLayout>

    );

}

export default Papers;