import { useState } from "react";
import { Search } from "lucide-react";

export default function SearchBar({ onSearch }) {

    const [query, setQuery] = useState("");

    const handleSearch = () => {
        if (!query.trim()) return;
        onSearch(query);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            handleSearch();
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-8">

            <div className="flex flex-col lg:flex-row gap-4 items-stretch">

                <div className="relative flex-1">

                    <Search
                        size={20}
                        className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                    />

                    <input
                        type="text"
                        value={query}
                        placeholder="Search research topics (e.g. Artificial Intelligence)"
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className="
                            w-full
                            h-14
                            pl-12
                            pr-4
                            rounded-xl
                            border
                            border-gray-300
                            text-base
                            focus:outline-none
                            focus:ring-2
                            focus:ring-blue-500
                            focus:border-blue-500
                            transition
                        "
                    />

                </div>

                <button
                    onClick={handleSearch}
                    className="
                        h-14
                        px-8
                        rounded-xl
                        bg-blue-600
                        hover:bg-blue-700
                        text-white
                        font-semibold
                        shadow-md
                        transition-all
                        duration-200
                        whitespace-nowrap
                        hover:shadow-lg
                        active:scale-95
                    "
                >
                    Search
                </button>

            </div>

        </div>
    );
}