from app.services.openalex_service import search_author

result = search_author("Andrew Ng")

print(result["results"][0]["display_name"])