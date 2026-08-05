import { useMemo } from "react";
import { Wordcloud } from "@visx/wordcloud";


const COLORS = [
    "#2563EB",
    "#0EA5E9",
    "#8B5CF6",
    "#14B8A6",
    "#F97316",
    "#EC4899",
    "#6366F1"
];

export default function TopicWordCloud({ graph }) {

    const width = 1100;
    const height = 600;

    const words = useMemo(() => {

        if (!graph?.nodes || !graph?.edges) return [];

        const degree = {};

        graph.nodes.forEach(node => {
            degree[node.id] = 0;
        });

        graph.edges.forEach(edge => {

            if (degree[edge.source] !== undefined)
                degree[edge.source]++;

            if (degree[edge.target] !== undefined)
                degree[edge.target]++;

        });

        return graph.nodes.map(node => ({

            text: node.label || node.id,

            value: Math.max(degree[node.id], 1)

        }));

    }, [graph]);

    if (words.length === 0) {

        return (

            <div className="bg-white rounded-3xl shadow-xl p-8">

                <h2 className="text-3xl font-bold">
                    Research Keywords
                </h2>

                <p className="text-gray-500 mt-3">
                    No keywords available.
                </p>

            </div>

        );

    }

    return (

        <div className="bg-white rounded-3xl shadow-xl border border-gray-200 p-8">

            <div className="mb-6">

                <h2 className="text-3xl font-bold text-gray-800">

                    Research Keywords

                </h2>

                <p className="text-gray-500 mt-2">

                    Frequently connected topics

                </p>

            </div>

            <div className="flex justify-center items-center">

                <svg
    width={width}
    height={height}
    viewBox={`0 0 ${width} ${height}`}
>

    <Wordcloud
        words={words}
        width={width - 100}
        height={height - 100}
        font="Inter"
        padding={8}
        spiral="archimedean"
        rotate={() => 0}
        random={() => 0.5}
        fontSize={(word) => Math.min(42, 18 + word.value * 2)}
    >

        {(cloudWords) => {

            if (!cloudWords.length) return null;

            const minX = Math.min(...cloudWords.map(w => w.x));
            const maxX = Math.max(...cloudWords.map(w => w.x));
            const minY = Math.min(...cloudWords.map(w => w.y));
            const maxY = Math.max(...cloudWords.map(w => w.y));

            const cloudWidth = maxX - minX;
            const cloudHeight = maxY - minY;

            const offsetX = (width - cloudWidth) / 2 - minX;
            const offsetY = (height - cloudHeight) / 2 - minY;

            return cloudWords.map((word, i) => (

                <text
                    key={word.text}
                    x={word.x + offsetX}
                    y={word.y + offsetY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    transform={`rotate(${word.rotate}, ${word.x + offsetX}, ${word.y + offsetY})`}
                    fontSize={word.size}
                    fontFamily={word.font}
                    fill={COLORS[i % COLORS.length]}
                    style={{
                        cursor: "pointer",
                        transition: "0.3s"
                    }}
                >
                    {word.text}
                </text>

            ));

        }}

    </Wordcloud>

</svg>

            </div>

        </div>

    );

}