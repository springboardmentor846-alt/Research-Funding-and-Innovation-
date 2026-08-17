import { Sparkles } from "lucide-react";

export default function AIInsight({ insight }) {

    if (!insight) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Key Insight
                </h2>

                <p className="text-gray-500 mt-2">
                    No insights available.
                </p>
            </div>
        );
    }

    return (
        <div className="rounded-2xl overflow-hidden shadow-xl border border-gray-200">

            <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 px-8 py-6">

                <div className="flex items-center gap-4">

                    <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">

                        <Sparkles size={28} className="text-white" />

                    </div>

                    <div>

                        <h2 className="text-2xl font-bold text-white">
                            Key Insight
                        </h2>

                        <p className="text-blue-100 mt-1">
                            Automatically generated research summary
                        </p>

                    </div>

                </div>

            </div>

            <div className="bg-white p-8">

                <div className="max-w-4xl">

                    <p className="text-gray-700 leading-8 text-[16px] whitespace-pre-line">

                        {insight}

                    </p>

                </div>

            </div>

        </div>
    );
}