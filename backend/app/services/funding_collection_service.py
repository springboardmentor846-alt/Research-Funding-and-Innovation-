from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.funding import FundingOpportunity


def normalize_funding_record(record: dict):

    deadline = record.get("deadline")

    if isinstance(deadline, str) and deadline:

        try:

            deadline = datetime.strptime(
                deadline,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            deadline = None

    return {

        "title":
            record.get("title"),

        "organization":
            record.get("organization"),

        "funding_type":
            record.get("funding_type"),

        "research_domain":
            record.get("research_domain"),

        "description":
            record.get("description"),

        "funding_amount":
            record.get("funding_amount"),

        "deadline":
            deadline,

        "official_link":
            record.get("official_link"),

        "country":
            record.get("country"),

        "eligible_countries":
            record.get("eligible_countries"),

        "international_applicants_allowed":
            record.get(
                "international_applicants_allowed",
                False
            ),

        "career_stage":
            record.get("career_stage"),

        "qualification":
            record.get("qualification"),

        "experience_required":
            record.get("experience_required"),

        "keywords":
            record.get("keywords"),

        "status":
            record.get(
                "status",
                "Open"
            ),
    }


def save_funding_opportunities(
    db: Session,
    records: list[dict]
):

    created = 0
    updated = 0
    skipped = 0

    for record in records:

        data = normalize_funding_record(
            record
        )

        # Minimum required information
        if (
            not data["title"]
            or not data["organization"]
        ):

            skipped += 1
            continue

        # Check whether same funding opportunity
        # already exists
        existing = db.scalar(

            select(
                FundingOpportunity
            ).where(

                FundingOpportunity.title
                == data["title"],

                FundingOpportunity.organization
                == data["organization"]
            )
        )

        if existing:

            for field, value in data.items():

                setattr(
                    existing,
                    field,
                    value
                )

            updated += 1

        else:

            opportunity = FundingOpportunity(
                **data
            )

            db.add(
                opportunity
            )

            created += 1

    db.commit()

    return {

        "processed":
            len(records),

        "created":
            created,

        "updated":
            updated,

        "skipped":
            skipped,
    }