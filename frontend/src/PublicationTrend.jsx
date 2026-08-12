import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function PublicationTrend() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/v1/profile/publications/trend"
        );
        setData(response.data);
      } catch (err) {
        setError("Could not load publication trend");
      }
    };

    fetchTrend();
  }, []);

  return (
    <div>
      {error && <p className="dash-error">{error}</p>}

      {!error && data.length === 0 && (
        <p className="dash-empty">No publication data yet.</p>
      )}

      {data.length > 0 && (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data}>
            <XAxis
              dataKey="year"
              stroke="#5B6578"
              tick={{ fontFamily: "Inter", fontSize: 12 }}
            />
            <YAxis
              allowDecimals={false}
              stroke="#5B6578"
              tick={{ fontFamily: "Inter", fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                fontFamily: "Inter",
                fontSize: 13,
                borderRadius: 8,
                border: "1px solid #E1E5EC",
              }}
            />
            <Bar dataKey="count" fill="#1F9E8E" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default PublicationTrend;
