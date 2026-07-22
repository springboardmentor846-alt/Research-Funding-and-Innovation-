from app.services.lens_service import search_patents

data = search_patents(
    "Artificial Intelligence"
)

print(data)