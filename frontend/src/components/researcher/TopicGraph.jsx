import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function TopicGraph({ graph }) {
    const containerRef = useRef(null);
    const graphRef = useRef();

    const [size, setSize] = useState({
        width: 800,
        height: 600
    });

    useEffect(() => {
        function updateSize() {
            if (!containerRef.current) return;

            setSize({
                width: containerRef.current.offsetWidth,
                height: 600
            });
        }

        updateSize();

        window.addEventListener("resize", updateSize);

        return () => window.removeEventListener("resize", updateSize);
    }, []);

    useEffect(() => {
        if (graphRef.current && graph?.nodes?.length) {
            setTimeout(() => {
                graphRef.current.zoomToFit(500, 80);
            }, 500);
        }
    }, [graph]);

    if (!graph || !graph.nodes || graph.nodes.length === 0) {
        return (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Topic Relationship Graph
                </h2>

                <p className="text-gray-500 mt-2">
                    No topic graph available.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Topic Relationship Graph
                </h2>

                <p className="text-gray-500 mt-1">
                    Interactive visualization of related research concepts.
                </p>
            </div>

            <div
                ref={containerRef}
                className="w-full h-[600px] rounded-xl overflow-hidden border border-gray-200"
            >
                <ForceGraph2D
                    ref={graphRef}
                    width={size.width}
                    height={size.height}
                    graphData={{
                        nodes: graph.nodes,
                        links: graph.edges
                    }}
                    nodeLabel="id"
                    nodeRelSize={7}
                    cooldownTicks={150}
                    linkDirectionalParticles={1}
                    linkDirectionalParticleSpeed={0.0025}
                    backgroundColor="#ffffff"
                    d3VelocityDecay={0.25}
                    d3AlphaDecay={0.03}
                    nodeCanvasObject={(node, ctx) => {
                        const label = node.id;

                        ctx.beginPath();
                        ctx.arc(node.x, node.y, 7, 0, 2 * Math.PI);
                        ctx.fillStyle = "#2563eb";
                        ctx.fill();

                        ctx.font = "11px Arial";
                        ctx.fillStyle = "#1f2937";
                        ctx.fillText(label, node.x + 10, node.y + 4);
                    }}
                    onEngineStop={() => graphRef.current?.zoomToFit(400, 80)}
                />
            </div>
        </div>
    );
}