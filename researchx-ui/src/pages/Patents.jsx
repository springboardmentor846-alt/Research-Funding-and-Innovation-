import { useEffect, useState } from "react";
import axios from "axios";
import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import { FileText } from "lucide-react";

export default function Patents() {
  const [patents, setPatents] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/patents/")
      .then((res) => setPatents(res.data))
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8">

        <Header
  title="Patents"
  subtitle="Manage research patents."
/>

        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6">

          <div className="flex items-center gap-3 mb-6">

            <FileText className="text-cyan-400 w-8 h-8"/>

            <h2 className="text-2xl font-bold text-white">
              Patent Repository
            </h2>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full">

              <thead className="bg-slate-800">

                <tr>

                  <th className="text-left px-5 py-4 text-slate-300">
                    Patent
                  </th>

                  <th className="text-left px-5 py-4 text-slate-300">
                    Domain
                  </th>

                  <th className="text-left px-5 py-4 text-slate-300">
                    Country
                  </th>

                  <th className="text-left px-5 py-4 text-slate-300">
                    Status
                  </th>

                  <th className="text-left px-5 py-4 text-slate-300">
                    Citations
                  </th>

                </tr>

              </thead>

              <tbody>

                {patents.map((patent) => (

                  <tr
                    key={patent.id}
                    className="border-b border-slate-800 hover:bg-slate-800"
                  >

                    <td className="px-5 py-4 text-white">
                      {patent.patent_title}
                    </td>

                    <td className="px-5 py-4 text-cyan-300">
                      {patent.technology_domain}
                    </td>

                    <td className="px-5 py-4 text-slate-300">
                      {patent.country}
                    </td>

                    <td className="px-5 py-4">

                      <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full">
                        {patent.status}
                      </span>

                    </td>

                    <td className="px-5 py-4 text-yellow-400">
                      {patent.citation_count}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>

      </main>

    </div>
  );
}