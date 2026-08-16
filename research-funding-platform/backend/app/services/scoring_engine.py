from typing import Dict, Any

class InnovationScoringEngine:
    @staticmethod
    def calculate_score(
        novelty: float,
        patent_strength: float,
        tech_maturity: float,
        market_potential: float,
        funding_relevance: float
    ) -> Dict[str, Any]:
        """
        Calculates weighted multi-factor innovation score (0 to 100).
        """
        # Ensure values are within 0-100 range
        n = max(0.0, min(100.0, float(novelty)))
        ps = max(0.0, min(100.0, float(patent_strength)))
        tm = max(0.0, min(100.0, float(tech_maturity)))
        mp = max(0.0, min(100.0, float(market_potential)))
        fr = max(0.0, min(100.0, float(funding_relevance)))

        overall_score = round(
            (0.25 * n) + (0.20 * ps) + (0.20 * tm) + (0.20 * mp) + (0.15 * fr), 2
        )

        recommendations = []
        if n < 60:
            recommendations.append("Consider performing a comprehensive prior-art search to refine research novelty.")
        if ps < 60:
            recommendations.append("Strengthen intellectual property portfolio with provisional patent applications or claim broadening.")
        if tm < 50:
            recommendations.append("Advance Technology Readiness Level (TRL) through bench scale prototyping and experimental validation.")
        if mp < 65:
            recommendations.append("Conduct commercial market validation and identify target industry early adopters.")
        if fr < 70:
            recommendations.append("Align core proposal objectives with federal and private grant priority focus areas.")
        
        if overall_score >= 80:
            recommendations.append("High commercial potential! Recommended for fast-track spin-off or technology licensing.")
        elif not recommendations:
            recommendations.append("Well-balanced innovation profile across technical and market dimensions.")

        rec_str = " | ".join(recommendations)

        return {
            "novelty_score": n,
            "patent_strength": ps,
            "tech_maturity": tm,
            "market_potential": mp,
            "funding_relevance": fr,
            "overall_score": overall_score,
            "recommendations": rec_str
        }

scoring_engine = InnovationScoringEngine()
