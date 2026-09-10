import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function PatentTrend() {
  const [data, setData] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const response = await axios.get(
          "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/patents/trend"
        );
        setData(response.data);
      } catch (err) {
        setError("Could not load patent trend");
      }
    };

    fetchTrend();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (data.length === 0) {
    return <p className="dash-empty">No patent data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <XAxis dataKey="year" stroke="#5B6578" tick={{ fontFamily: "Inter", fontSize: 12 }} />
        <YAxis allowDecimals={false} stroke="#5B6578" tick={{ fontFamily: "Inter", fontSize: 12 }} />
        <Tooltip contentStyle={{ fontFamily: "Inter", fontSize: 13, borderRadius: 8, border: "1px solid #E1E5EC" }} />
        <Bar dataKey="count" fill="#E8A33D" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default PatentTrend;

