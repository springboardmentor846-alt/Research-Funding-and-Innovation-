from collections import Counter

from sqlalchemy import select

from app.models.publication import Publication


def publication_statistics(db, profile):

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id == profile.id
        )
    ).all()

    yearly = Counter()

    publishers = Counter()

    journals = Counter()

    publication_types = Counter()

    for publication in publications:

        if publication.publication_date:
            yearly[publication.publication_date.year] += 1

        if publication.publisher:
            publishers[publication.publisher] += 1

        if publication.journal_or_conference:
            journals[publication.journal_or_conference] += 1

        if publication.publication_type:
            publication_types[publication.publication_type] += 1

    return {

        "total_publications": len(publications),

        "publication_trend": dict(
            sorted(yearly.items())
        ),

        "top_publishers": publishers.most_common(5),

        "top_journals": journals.most_common(5),

        "publication_types": publication_types.most_common(5)
    }