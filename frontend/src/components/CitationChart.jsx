import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function CitationChart({ data }) {

    return (

        <div
            style={{
                width: "100%",
                height: 350,
                marginTop: "40px"
            }}
        >

            <h2>Citation Trend</h2>

            <ResponsiveContainer>

                <LineChart data={data}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="year" />

                    <YAxis />

                    <Tooltip />

                    <Line
                        type="monotone"
                        dataKey="citations"
                    />

                </LineChart>

            </ResponsiveContainer>

        </div>

    );

}

export default CitationChart;