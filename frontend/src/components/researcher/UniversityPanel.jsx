export default function UniversityPanel({ universities }) {

    if (!universities || universities.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Top Universities
                </h2>

                <p className="text-gray-500 mt-2">
                    No university statistics available.
                </p>
            </div>
        );
    }

    const maxCount = Math.max(
        ...universities.map(university => university.count)
    );

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 h-[560px] flex flex-col">

            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Top Universities
                </h2>

                <p className="text-gray-500 mt-1">
                    Publications by institution
                </p>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 space-y-5">

                {universities.slice(0, 10).map((university, index) => (

                    <div
                        key={university.university}
                        className="bg-gray-50 rounded-xl p-4 border border-gray-100 hover:shadow-md transition"
                    >

                        <div className="flex justify-between items-start mb-3">

                            <div className="flex gap-3 flex-1 min-w-0">

                                <div className="w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center font-semibold text-sm flex-shrink-0">

                                    {index + 1}

                                </div>

                                <div className="min-w-0 flex-1">

                                    <p className="font-semibold text-gray-800 break-words leading-6">

                                        {university.university}

                                    </p>

                                </div>

                            </div>

                            <span className="text-green-600 font-bold text-lg ml-4 flex-shrink-0">

                                {university.count}

                            </span>

                        </div>

                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">

                            <div
                                className="h-full bg-green-600 rounded-full transition-all duration-700"
                                style={{
                                    width: `${(university.count / maxCount) * 100}%`
                                }}
                            />

                        </div>

                    </div>

                ))}

            </div>

        </div>
    );
}