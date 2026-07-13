import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend
} from "recharts";

const COLORS = [
    "#2563EB",
    "#14B8A6",
    "#F59E0B",
    "#8B5CF6",
    "#EF4444"
];

function PatentClusterChart({ data }) {

    return (

        <ResponsiveContainer
            width="100%"
            height={320}
        >

            <PieChart>

                <Pie

                    data={data}

                    dataKey="Patent Count"

                    nameKey="Technology Domain"

                    outerRadius={110}

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

export default PatentClusterChart;