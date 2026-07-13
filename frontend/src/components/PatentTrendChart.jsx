import {
    ResponsiveContainer,
    LineChart,
    Line,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip
} from "recharts";

function PatentTrendChart({ data }) {

    return (

        <ResponsiveContainer
            width="100%"
            height={320}
        >

            <LineChart data={data}>

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="Filing Date" />

                <YAxis />

                <Tooltip />

                <Line
                    type="monotone"
                    dataKey="Patents Filed"
                    stroke="#2563EB"
                    strokeWidth={3}
                />

            </LineChart>

        </ResponsiveContainer>

    );

}

export default PatentTrendChart;