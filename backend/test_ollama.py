from app.services.ollama_service import summarize_research

result = summarize_research(
    title="Artificial Intelligence in Healthcare",
    abstract="""
Artificial Intelligence is increasingly used for disease diagnosis,
medical image analysis, and personalized treatment planning.
"""
)

print(result)