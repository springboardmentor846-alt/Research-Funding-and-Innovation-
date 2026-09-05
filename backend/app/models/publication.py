from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("research_profiles.id"), nullable=False)

    title = Column(String, nullable=False)
    authors = Column(String)
    year = Column(String)
    source = Column(String)      # journal/conference name
    link = Column(String)        # URL to paper

    pdf_path = Column(String, nullable=True)          # uploaded PDF file path, if any
    source_type = Column(String, default="own", nullable=False)
    # source_type: "own" = added/authored by the researcher (My Publications)
    #              "external" = imported from OpenAlex for reference (Research Library)

    profile = relationship("ResearchProfile", backref="publication_list")