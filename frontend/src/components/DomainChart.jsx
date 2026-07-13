import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    Legend
} from "recharts";

const COLORS = [
    "#0088FE",
    "#00C49F",
    "#FFBB28",
    "#FF8042",
    "#A28CFF",
    "#FF6699"
];

function DomainChart({ data }) {

    return (

        <div
            style={{
                width: "100%",
                height: 400,
                marginTop: "40px"
            }}
        >

            <h2>Research Domain Distribution</h2>

            <ResponsiveContainer>

                <PieChart>

                    <Pie
                        data={data}
                        dataKey="papers"
                        nameKey="domain"
                        outerRadius={120}
                        label
                    >

                        {
                            data.map((entry, index) => (
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

        </div>

    );

}

export default DomainChart;