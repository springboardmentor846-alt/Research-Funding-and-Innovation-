import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    ResponsiveContainer
} from "recharts";

export default function TrendChart({ data }) {

    if (!data || data.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Publication Trend
                </h2>

                <p className="text-gray-500 mt-2">
                    No publication trend available.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">

            <div className="mb-6">

                <h2 className="text-2xl font-bold text-gray-800">
                    Publication Trend
                </h2>

                <p className="text-gray-500 mt-1">
                    Number of publications over the years
                </p>

            </div>

            <div className="w-full h-[420px]">

                <ResponsiveContainer width="100%" height="100%">

                    <LineChart
                        data={data}
                        margin={{
                            top: 20,
                            right: 30,
                            left: 10,
                            bottom: 10
                        }}
                    >

                        <CartesianGrid
                            strokeDasharray="4 4"
                            stroke="#E5E7EB"
                        />

                        <XAxis
                            dataKey="year"
                            tick={{ fontSize: 13 }}
                            tickLine={false}
                            axisLine={false}
                        />

                        <YAxis
                            tick={{ fontSize: 13 }}
                            tickLine={false}
                            axisLine={false}
                        />

                        <Tooltip
                            contentStyle={{
                                borderRadius: "12px",
                                border: "1px solid #E5E7EB",
                                boxShadow: "0 6px 18px rgba(0,0,0,0.12)"
                            }}
                        />

                        <Line
                            type="monotone"
                            dataKey="count"
                            stroke="#2563EB"
                            strokeWidth={3}
                            dot={{
                                r: 5,
                                fill: "#2563EB"
                            }}
                            activeDot={{
                                r: 8
                            }}
                        />

                    </LineChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}