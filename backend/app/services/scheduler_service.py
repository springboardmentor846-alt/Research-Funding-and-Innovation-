from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.openalex_service import OpenAlexService
from app.models.research_paper import ResearchPaper


class SchedulerService:

    def __init__(self):

        self.scheduler = BackgroundScheduler()

        self.openalex = OpenAlexService()

    async def sync_ai_papers(self):

        db: Session = SessionLocal()

        try:

            papers = await self.openalex.search(
                "Artificial Intelligence"
            )

            for paper in papers["results"]:

                existing = db.query(
                    ResearchPaper
                ).filter(
                    ResearchPaper.openalex_id == paper["id"]
                ).first()

                if existing:
                    continue

                authors = ", ".join(

                    author["author"]["display_name"]

                    for author in paper.get(
                        "authorships",
                        []
                    )

                )

                journal = ""

                if paper.get("primary_location"):

                    source = paper["primary_location"].get("source")

                    if source:

                        journal = source.get(
                            "display_name",
                            ""
                        )

                new_paper = ResearchPaper(

                    openalex_id=paper["id"],

                    title=paper.get("title"),

                    abstract="",

                    publication_year=paper.get(
                        "publication_year"
                    ),

                    citation_count=paper.get(
                        "cited_by_count"
                    ),

                    doi=paper.get("doi"),

                    journal=journal,

                    authors=authors,

                    institutions="",

                    research_domain="Artificial Intelligence"

                )

                db.add(new_paper)

            db.commit()

            print("Automatic OpenAlex Sync Completed")

        finally:

            db.close()

    def start(self):

        self.scheduler.add_job(

            lambda: __import__("asyncio").run(
                self.sync_ai_papers()
            ),

            trigger="interval",

            hours=24

        )

        self.scheduler.start()