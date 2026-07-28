import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid
} from "recharts";

function ResearchImpactChart({ data }) {

    return (

        <ResponsiveContainer width="100%" height={300}>

            <BarChart data={data}>

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="Researcher" />

                <YAxis />

                <Tooltip />

                <Bar
                    dataKey="Research Novelty"
                    fill="#1976d2"
                />

            </BarChart>

        </ResponsiveContainer>

    );

}

export default ResearchImpactChart;