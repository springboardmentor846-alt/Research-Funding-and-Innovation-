import re
from typing import List, Dict, Any

class FundingMatchingEngine:
    @staticmethod
    def match_eligibility(user_domains: str, user_keywords: str, grant: Any) -> float:
        """
        Computes a match score percentage (0-100%) between a researcher profile and a funding grant.
        """
        if not user_domains and not user_keywords:
            return 50.0

        user_tokens = set(re.findall(r'\w+', (f"{user_domains or ''} {user_keywords or ''}").lower()))
        if not user_tokens:
            return 50.0

        grant_text = f"{grant.title} {grant.description} {grant.eligibility_criteria} {grant.keywords or ''}".lower()
        grant_tokens = set(re.findall(r'\w+', grant_text))

        intersection = user_tokens.intersection(grant_tokens)
        match_ratio = len(intersection) / float(len(user_tokens)) if user_tokens else 0.0

        score = min(99.0, max(35.0, round(match_ratio * 100.0 + 40.0, 1)))
        return score

    @classmethod
    def rank_funding_for_profile(cls, grants: List[Any], domains: str, keywords: str) -> List[Dict[str, Any]]:
        results = []
        for grant in grants:
            score = cls.match_eligibility(domains, keywords, grant)
            results.append({
                "grant": grant,
                "match_score": score,
                "match_tier": "High" if score >= 80 else ("Medium" if score >= 60 else "Eligible")
            })
        
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results

matching_engine = FundingMatchingEngine()
