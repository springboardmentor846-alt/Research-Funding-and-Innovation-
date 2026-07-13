import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function TRLChart({ data }) {

    return (

        <div
            style={{
                width: "100%",
                height: 400,
                marginTop: "40px"
            }}
        >

            <h2>TRL Level Distribution</h2>

            <ResponsiveContainer>

                <BarChart data={data}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="trl_level" />

                    <YAxis />

                    <Tooltip />

                    <Bar dataKey="papers" />

                </BarChart>

            </ResponsiveContainer>

        </div>

    );

}

export default TRLChart;