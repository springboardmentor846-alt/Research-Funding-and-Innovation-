import { useState } from "react";

import { getResearchTrends } from "../../api/researcher/researchTrends";

import SearchBar from "../../components/researcher/SearchBar";
import TrendChart from "../../components/researcher/TrendChart";
import CountryPanel from "../../components/researcher/CountryPanel";
import UniversityPanel from "../../components/researcher/UniversityPanel";
//import TopicWordCloud from "../components/TopicWordCloud";
import AIInsight from "../../components/researcher/AIInsight";

export default function ResearchTrends() {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);

    const searchResearch = async (query) => {

        try {

            setLoading(true);

            const response = await getResearchTrends(query);

            setData(response);

        }

        catch (error) {

            console.error(error);

            alert("Failed to fetch research trends.");

        }

        finally {

            setLoading(false);

        }

    };

    return (

        <div className="max-w-screen-2xl mx-auto px-6 lg:px-10 py-8">

            {/* Header */}

            <div className="mb-10">

                <h1 className="text-4xl lg:text-5xl font-bold text-gray-900">

                    Research Trends Dashboard

                </h1>

                <p className="text-gray-500 text-lg mt-3 max-w-3xl">

                    Discover publication trends, leading countries,
                    top universities and emerging research topics.

                </p>

            </div>

            {/* Search */}

            <SearchBar onSearch={searchResearch} />

            {/* Loading */}

            {

                loading && (

                    <div className="flex justify-center py-24">

                        <div className="w-14 h-14 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>

                    </div>

                )

            }

            {

                !loading && data && (

                    <>

                        {/* Summary */}

                        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">

                            <div className="bg-white rounded-2xl shadow-lg border p-8">

                                <p className="text-gray-500">

                                    Publications

                                </p>

                                <h2 className="text-4xl font-bold text-blue-600 mt-4">

                                    {

                                        data.trend.reduce(
                                            (sum, item) => sum + item.count,
                                            0
                                        )

                                    }

                                </h2>

                            </div>

                            <div className="bg-white rounded-2xl shadow-lg border p-8">

                                <p className="text-gray-500">

                                    Countries

                                </p>

                                <h2 className="text-4xl font-bold text-green-600 mt-4">

                                    {data.countries.length}

                                </h2>

                            </div>

                            <div className="bg-white rounded-2xl shadow-lg border p-8">

                                <p className="text-gray-500">

                                    Universities

                                </p>

                                <h2 className="text-4xl font-bold text-purple-600 mt-4">

                                    {data.universities.length}

                                </h2>

                            </div>

                            <div className="bg-white rounded-2xl shadow-lg border p-8">

                                <p className="text-gray-500">

                                    Research Topics

                                </p>

                                <h2 className="text-4xl font-bold text-orange-500 mt-4">

                                    {data.topicGraph.nodes.length}

                                </h2>

                            </div>

                        </div>

                        {/* Trend Chart */}

                        <section className="mb-10">

                            <TrendChart
                                data={data.trend}
                            />

                        </section>

                        {/* Countries + Universities */}

                        <section className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-10">

                            <CountryPanel
                                countries={data.countries}
                            />

                            <UniversityPanel
                                universities={data.universities}
                            />

                        </section>

                        {/* Topic Graph */}

                        {/* <section className="mb-10">

                            <TopicWordCloud
                                graph={data.topicGraph}
                            />

                        </section> */}

                        {/* AI Insight */}

                        <section>

                            <AIInsight
                                insight={data.aiInsight}
                            />

                        </section>

                    </>

                )

            }

            {

                !loading && !data && (

                    <div className="bg-white rounded-2xl shadow-lg border border-dashed p-16 text-center mt-10">

                        <h2 className="text-3xl font-bold text-gray-800">

                            Search Any Research Topic

                        </h2>

                        <p className="text-gray-500 mt-4">

                            Try one of these popular research areas

                        </p>

                        <div className="flex flex-wrap justify-center gap-3 mt-8">

                            <span className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full">

                                Artificial Intelligence

                            </span>

                            <span className="bg-green-100 text-green-700 px-4 py-2 rounded-full">

                                Machine Learning

                            </span>

                            <span className="bg-purple-100 text-purple-700 px-4 py-2 rounded-full">

                                Blockchain

                            </span>

                            <span className="bg-orange-100 text-orange-700 px-4 py-2 rounded-full">

                                Quantum Computing

                            </span>

                        </div>

                    </div>

                )

            }

        </div>

    );

}