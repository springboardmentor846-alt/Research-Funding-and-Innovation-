import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend
} from "recharts";

const COLORS = [
    "#1976d2",
    "#43a047",
    "#ff9800",
    "#d32f2f"
];

function TechnologyReadinessChart({ data }) {

    return (

        <ResponsiveContainer width="100%" height={300}>

            <PieChart>

                <Pie
                    data={data}
                    dataKey="Technology Maturity"
                    nameKey="Researcher"
                    outerRadius={100}
                    label
                >

                    {

                        data.map((entry,index)=>(

                            <Cell
                                key={index}
                                fill={COLORS[index % COLORS.length]}
                            />

                        ))

                    }

                </Pie>

                <Tooltip />

                <Legend />

            </PieChart>

        </ResponsiveContainer>

    );

}

export default TechnologyReadinessChart;