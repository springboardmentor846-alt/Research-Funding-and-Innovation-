"""
Patent Landscape & IPC Cluster Service
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.patent import Patent


class PatentService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_landscape_analytics(self) -> Dict[str, Any]:
        """
        Aggregates patent database records for landscape maps, assignee distribution, IPC code grouping, and clusters.
        """
        result = await self.db.execute(select(Patent))
        patents = result.scalars().all()

        total_patents = len(patents)
        assignees_count: Dict[str, int] = {}
        ipc_count: Dict[str, int] = {}
        domain_count: Dict[str, int] = {}
        clusters: Dict[str, List[Patent]] = {}

        for p in patents:
            assignees_count[p.assignee] = assignees_count.get(p.assignee, 0) + 1
            ipc_count[p.ipc_classification] = ipc_count.get(p.ipc_classification, 0) + 1
            domain_count[p.technology_domain] = domain_count.get(p.technology_domain, 0) + 1
            
            c_id = p.cluster_id or "Unclustered"
            if c_id not in clusters:
                clusters[c_id] = []
            clusters[c_id].append(p)

        cluster_summaries = []
        for cid, plist in clusters.items():
            top_assignees = list(set(p.assignee for p in plist))[:3]
            cluster_summaries.append({
                "cluster_id": cid,
                "cluster_name": plist[0].technology_domain if plist else "General",
                "ipc_code": plist[0].ipc_classification if plist else "G06",
                "patent_count": len(plist),
                "top_assignees": top_assignees,
                "sample_patents": [
                    {
                        "id": str(p.id),
                        "patent_number": p.patent_number,
                        "title": p.title,
                        "assignee": p.assignee,
                        "ipc_classification": p.ipc_classification,
                        "technology_domain": p.technology_domain,
                        "citation_count": p.citation_count,
                        "abstract": p.abstract
                    } for p in plist[:5]
                ]
            })

        return {
            "total_patents_analyzed": total_patents,
            "top_assignees_breakdown": dict(sorted(assignees_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "ipc_classification_distribution": ipc_count,
            "technology_domain_breakdown": domain_count,
            "patent_clusters": cluster_summaries
        }
