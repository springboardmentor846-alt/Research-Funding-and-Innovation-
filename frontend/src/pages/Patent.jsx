import { useEffect, useState } from "react";
import {
    Grid,
    Paper,
    Typography,
    Button,
    Table,
    TableHead,
    TableBody,
    TableRow,
    TableCell,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from "@mui/material";

import DashboardLayout from "../layouts/DashboardLayout";
import PatentTrendChart from "../components/PatentTrendChart";
import PatentClusterChart from "../components/PatentClusterChart";
import PatentAnalytics from "../components/PatentAnalytics";

import {
    getPatents,
    getPatentAnalytics,
    getPatentClusters,
    getPatentTrends,
    getInnovationMap,
    addPatent
} from "../services/patentApi";

function Patent() {

    const [patents, setPatents] = useState([]);

    const [analytics, setAnalytics] = useState({});

    const [clusters, setClusters] = useState([]);

    const [trends, setTrends] = useState([]);

    const [innovationMap, setInnovationMap] = useState({});

    const [open, setOpen] = useState(false);

    const [form, setForm] = useState({
        title: "",
        assignee: "",
        filing_date: "",
        patent_classification: "",
        technology_domain: "",
        citation_count: 0
    });

    async function loadData() {

        try {

            setPatents(await getPatents());

            setAnalytics(await getPatentAnalytics());

            setClusters(await getPatentClusters());

            setTrends(await getPatentTrends());

            setInnovationMap(await getInnovationMap());

        }

        catch (err) {

            console.log(err);

        }

    }

    useEffect(() => {

        loadData();

    }, []);

    async function handleSubmit() {

        await addPatent(form);

        setOpen(false);

        loadData();

    }

    return (

        <DashboardLayout>

            <Typography
                variant="h4"
                fontWeight="bold"
                mb={4}
            >

                Patent Intelligence Dashboard

            </Typography>

            <Grid container spacing={3}>

                <Grid item xs={12} md={3}>

                    <StatCard
                        title="Total Patents"
                        value={analytics["Total Patents"]}
                    />

                </Grid>

                <Grid item xs={12} md={3}>

                    <StatCard
                        title="Total Citations"
                        value={analytics["Total Citations"]}
                    />

                </Grid>

                <Grid item xs={12} md={3}>

                    <StatCard
                        title="Average Citations"
                        value={analytics["Average Citations"]}
                    />

                </Grid>

                <Grid item xs={12} md={3}>

                    <StatCard
                        title="Top Patent"
                        value={analytics["Top Patent"]?.title}
                    />

                </Grid>

            </Grid>

            <Grid
                container
                spacing={3}
                mt={2}
            >

                <Grid item xs={12} md={7}>

                    <Paper sx={{ p:3 }}>

                        <Typography
                            variant="h6"
                            mb={2}
                        >

                            Patent Trends

                        </Typography>

                        <PatentTrendChart
                            data={trends}
                        />

                    </Paper>

                </Grid>

                <Grid item xs={12} md={5}>

                    <Paper sx={{ p:3 }}>

                        <Typography
                            variant="h6"
                            mb={2}
                        >

                            Patent Clusters

                        </Typography>

                        <PatentClusterChart
                            data={clusters}
                        />

                    </Paper>

                </Grid>

            </Grid>

            <Paper
                sx={{
                    mt:4,
                    p:3
                }}
            >

                <Typography
                    variant="h6"
                    mb={2}
                >

                    Innovation Map

                </Typography>

                {

                    Object.keys(innovationMap).map(domain => (

                        <Paper
                            key={domain}
                            sx={{
                                p:2,
                                mb:2,
                                bgcolor:"#F5F7FB"
                            }}
                        >

                            <Typography
                                fontWeight="bold"
                                mb={1}
                            >

                                {domain}

                            </Typography>

                            {

                                innovationMap[domain].map((item,index)=>(

                                    <Typography key={index}>

                                        • {item.Patent}
                                        {" | "}
                                        {item.Assignee}
                                        {" | "}
                                        {item.Citations} Citations

                                    </Typography>

                                ))

                            }

                        </Paper>

                    ))

                }

            </Paper>

            <Paper
                sx={{
                    mt:4,
                    p:3
                }}
            >

                <Grid
                    container
                    justifyContent="space-between"
                    mb={2}
                >

                    <Typography variant="h6">

                        Patent List

                    </Typography>

                    <Button
                        variant="contained"
                        onClick={() => setOpen(true)}
                    >

                        Add Patent

                    </Button>

                </Grid>

                <Table>

                    <TableHead>

                        <TableRow>

                            <TableCell>Title</TableCell>

                            <TableCell>Technology</TableCell>

                            <TableCell>Classification</TableCell>

                            <TableCell>Assignee</TableCell>

                            <TableCell>Citations</TableCell>

                            <TableCell>Filing Date</TableCell>

                        </TableRow>

                    </TableHead>

                    <TableBody>

                        {

                            patents.map((item)=>(

                                <TableRow key={item.id}>

                                    <TableCell>{item.title}</TableCell>

                                    <TableCell>{item.technology_domain}</TableCell>

                                    <TableCell>{item.patent_classification}</TableCell>

                                    <TableCell>{item.assignee}</TableCell>

                                    <TableCell>{item.citation_count}</TableCell>

                                    <TableCell>{item.filing_date}</TableCell>

                                </TableRow>

                            ))

                        }

                    </TableBody>

                </Table>

            </Paper>

            <Dialog
                open={open}
                onClose={()=>setOpen(false)}
                fullWidth
            >

                <DialogTitle>

                    Add Patent

                </DialogTitle>

                <DialogContent>

                    {

                        Object.keys(form).map((key)=>(

                            <TextField

                                key={key}

                                margin="normal"

                                fullWidth

                                label={key.replaceAll("_"," ")}

                                value={form[key]}

                                onChange={(e)=>setForm({
                                    ...form,
                                    [key]:e.target.value
                                })}

                            />

                        ))

                    }

                </DialogContent>

                <DialogActions>

                    <Button
                        onClick={()=>setOpen(false)}
                    >

                        Cancel

                    </Button>

                    <Button
                        variant="contained"
                        onClick={handleSubmit}
                    >

                        Save

                    </Button>

                </DialogActions>

            </Dialog>

        </DashboardLayout>

    );

}

export default Patent;