import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function FundingChart({ data }) {

    return (

        <div
            style={{
                width: "100%",
                height: 400,
                marginTop: "40px"
            }}
        >

            <h2>Funding Distribution</h2>

            <ResponsiveContainer>

                <BarChart data={data}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="domain" />

                    <YAxis />

                    <Tooltip />

                    <Bar dataKey="fundings" />

                </BarChart>

            </ResponsiveContainer>

        </div>

    );

}

export default FundingChart;