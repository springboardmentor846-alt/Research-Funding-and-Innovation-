"""
Weighted Innovation Scoring Engine & Commercialization Advisory Generator
Formula:
Innovation Score = (Novelty * 0.30) + (Patent Strength * 0.20) + (Tech Maturity * 0.15) + (Market Potential * 0.20) + (Funding Relevance * 0.15)
"""

from typing import Dict, Any, Tuple, List


class InnovationScorerEngine:

    @staticmethod
    def calculate_weighted_score(
        novelty: float,
        patent_strength: float,
        tech_maturity: float,
        market_potential: float,
        funding_relevance: float
    ) -> float:
        """
        Calculates the standardized Innovation Score based on weighted metrics specified in page 5.
        """
        score = (
            (novelty * 0.30) +
            (patent_strength * 0.20) +
            (tech_maturity * 0.15) +
            (market_potential * 0.20) +
            (funding_relevance * 0.15)
        )
        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def generate_commercialization_recommendations(
        domain: str,
        total_score: float,
        tech_maturity: float,
        market_potential: float
    ) -> Dict[str, List[str]]:
        """
        Generates structured AI commercialization advisory based on technology readiness and market scores.
        """
        # Productization
        if tech_maturity >= 70:
            productization = [
                f"Prepare direct MVP commercial roll-out in {domain}.",
                "Initiate pilot customer deployments with corporate innovation partners.",
                "Establish ISO quality assurance and compliance certification frameworks."
            ]
        else:
            productization = [
                f"Conduct proof-of-concept testing in lab environment for {domain}.",
                "Focus on prototype validation and functional prototype testing (TRL 4-6).",
                "Apply for university/institutional translational research grants."
            ]

        # Licensing
        if market_potential >= 75:
            licensing = [
                f"Execute non-exclusive licensing agreements with tier-1 enterprise leaders in {domain}.",
                "Structure milestone-based royalty model (3-7% net sales revenue).",
                "File international PCT patent applications to safeguard licensing territory."
            ]
        else:
            licensing = [
                "Establish field-of-use restrictive licensing with targeted niche vendors.",
                "Offer research-use-only (RUO) software & algorithm licenses.",
                "Engage technology transfer office (TTO) for valuation assessment."
            ]

        # Startup Creation
        if total_score >= 75:
            startup = [
                "Incorporate a university spin-out or deep-tech startup entity.",
                "Target Y Combinator, NSF I-Corps, or specialized deep-tech accelerators.",
                "Recruit commercial co-founder with go-to-market execution track record."
            ]
        else:
            startup = [
                "Participate in incubator pre-seed ideation cohorts.",
                "Seek non-dilutive SBIR/STTR Phase I grant funding.",
                "Conduct customer discovery interviews with 30+ potential industry buyers."
            ]

        # Industry Partnerships
        partnerships = [
            f"Form joint development agreement (JDA) with established R&D centers in {domain}.",
            "Co-publish industry whitepapers to build market domain authority.",
            "Apply for joint industry-academic grant consortia (e.g. EU Horizon / NSF IUCRC)."
        ]

        return {
            "productization_recommendations": productization,
            "licensing_opportunities": licensing,
            "startup_creation_recommendations": startup,
            "industry_partnership_suggestions": partnerships
        }
