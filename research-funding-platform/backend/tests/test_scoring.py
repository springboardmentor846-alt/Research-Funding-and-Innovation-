from app.services.scoring_engine import scoring_engine

def test_innovation_score_calculation():
    result = scoring_engine.calculate_score(
        novelty=90.0,
        patent_strength=80.0,
        tech_maturity=70.0,
        market_potential=85.0,
        funding_relevance=95.0
    )
    # 0.25*90 + 0.20*80 + 0.20*70 + 0.20*85 + 0.15*95 = 22.5 + 16.0 + 14.0 + 17.0 + 14.25 = 83.75
    assert result["overall_score"] == 83.75
    assert "High commercial potential" in result["recommendations"]
