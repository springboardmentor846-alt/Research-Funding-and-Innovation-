import { useEffect, useState } from "react";
import axios from "axios";
import { Landmark, Search } from "lucide-react";

export default function FundingTable() {
  const [funding, setFunding] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/funding/")
      .then((res) => setFunding(res.data))
      .catch((err) => console.error(err));
  }, []);

  const filteredFunding = funding.filter((item) =>
    item.title.toLowerCase().includes(search.toLowerCase()) ||
    item.organization.toLowerCase().includes(search.toLowerCase()) ||
    item.research_domain.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="mt-8 bg-slate-900 border border-slate-700 rounded-2xl shadow-xl p-6">

      {/* Heading */}

      <div className="flex justify-between items-center mb-6 flex-wrap gap-4">

        <div className="flex items-center gap-3">

          <Landmark className="text-green-400 w-7 h-7" />

          <div>

            <h2 className="text-2xl font-bold text-white">
              Latest Funding Opportunities
            </h2>

            <p className="text-slate-400 text-sm">
              Explore available research grants and funding programs
            </p>

          </div>

        </div>

        {/* Search */}

        <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg border border-slate-700">

          <Search size={18} className="text-slate-400" />

          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent outline-none text-white placeholder:text-slate-500"
          />

        </div>

      </div>

      <div className="overflow-x-auto rounded-xl">

        <table className="w-full">

          <thead className="bg-slate-800 text-slate-300">

            <tr>

              <th className="px-5 py-4 text-left">#</th>

              <th className="px-5 py-4 text-left">Title</th>

              <th className="px-5 py-4 text-left">Organization</th>

              <th className="px-5 py-4 text-left">Domain</th>

              <th className="px-5 py-4 text-left">Amount</th>

              <th className="px-5 py-4 text-left">Status</th>

            </tr>

          </thead>

          <tbody>

            {filteredFunding.map((item, index) => (

              <tr
                key={item.id}
                className="border-b border-slate-800 hover:bg-slate-800/60 transition"
              >

                <td className="px-5 py-4 text-slate-300">
                  {index + 1}
                </td>

                <td className="px-5 py-4 font-medium text-white">
                  {item.title}
                </td>

                <td className="px-5 py-4 text-slate-300">
                  {item.organization}
                </td>

                <td className="px-5 py-4">

                  <span className="bg-cyan-500/20 text-cyan-300 px-3 py-1 rounded-full text-sm">
                    {item.research_domain}
                  </span>

                </td>

                <td className="px-5 py-4">

                  <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full font-semibold">
                    ₹ {Number(item.funding_amount).toLocaleString("en-IN")}
                  </span>

                </td>

                <td className="px-5 py-4">

                  <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm">
                    Open
                  </span>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

        {filteredFunding.length === 0 && (

          <div className="text-center py-8 text-slate-400">

            No funding opportunities found.

          </div>

        )}

      </div>

    </div>
  );
}