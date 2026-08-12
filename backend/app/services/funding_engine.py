"""
Grant Eligibility Matching Engine
"""

from typing import List, Dict, Any
from app.models.funding import FundingOpportunity


class FundingEngine:

    @staticmethod
    def calculate_eligibility_score(
        opportunity: FundingOpportunity,
        user_domains: List[str],
        user_keywords: List[str],
        applicant_role: str = "Researcher"
    ) -> Dict[str, Any]:
        """
        Calculates domain & keyword overlap match score for a funding grant.
        """
        user_domains_lower = set(d.lower() for d in user_domains)
        user_keywords_lower = set(k.lower() for k in user_keywords)

        grant_domains = set(d.lower() for d in (opportunity.target_domains or []))
        grant_keywords = set(k.lower() for k in (opportunity.target_keywords or []))

        matched_domains = list(user_domains_lower.intersection(grant_domains))
        matched_keywords = list(user_keywords_lower.intersection(grant_keywords))

        domain_score = (len(matched_domains) / max(1, len(grant_domains))) * 50.0
        keyword_score = (len(matched_keywords) / max(1, len(grant_keywords))) * 40.0

        # Role match bonus (10%)
        role_match = 10.0 if any(applicant_role.lower() in t.lower() for t in (opportunity.eligible_applicant_types or [])) else 5.0

        total_match_score = round(min(100.0, domain_score + keyword_score + role_match), 1)

        if total_match_score >= 75:
            status = "High Match"
            recs = ["Strong proposal match! Priority application recommended.", "Align specific grant keywords in Abstract."]
        elif total_match_score >= 50:
            status = "Medium Match"
            recs = ["Good synergy. Modify project scope to align with target grant criteria."]
        else:
            status = "Low Match"
            recs = ["Consider partnering with co-investigators in target domains to strengthen eligibility."]

        return {
            "grant_id": str(opportunity.id),
            "grant_title": opportunity.title,
            "agency": opportunity.agency,
            "match_score": total_match_score,
            "matched_domains": [d.capitalize() for d in matched_domains],
            "matched_keywords": [k.capitalize() for k in matched_keywords],
            "eligibility_status": status,
            "recommendations": recs
        }
