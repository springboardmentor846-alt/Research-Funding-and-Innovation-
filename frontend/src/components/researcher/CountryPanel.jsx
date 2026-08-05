export default function CountryPanel({ countries }) {

    if (!countries || countries.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Top Countries
                </h2>

                <p className="text-gray-500 mt-2">
                    No country statistics available.
                </p>
            </div>
        );
    }

    const maxCount = Math.max(...countries.map(country => country.count));

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-[560px] flex flex-col">

            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Top Countries
                </h2>

                <p className="text-gray-500 mt-1">
                    Publications by country
                </p>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 space-y-5">

                {countries.slice(0, 10).map((country, index) => (

                    <div
                        key={country.country}
                        className="bg-gray-50 rounded-xl p-4 border border-gray-100 hover:shadow-md transition"
                    >

                        <div className="flex justify-between items-center mb-3">

                            <div className="flex items-center gap-3">

                                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold text-sm">

                                    {index + 1}

                                </div>

                                <div>

                                    <p className="font-semibold text-gray-800">

                                        {country.country}

                                    </p>

                                </div>

                            </div>

                            <span className="text-blue-600 font-bold text-lg">

                                {country.count}

                            </span>

                        </div>

                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">

                            <div
                                className="h-full bg-blue-600 rounded-full transition-all duration-700"
                                style={{
                                    width: `${(country.count / maxCount) * 100}%`
                                }}
                            />

                        </div>

                    </div>

                ))}

            </div>

        </div>
    );
}