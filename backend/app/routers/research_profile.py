from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.dependencies import get_db, require_role
from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.user import User
from app.models.patent import Patent
from app.models.publication import Publication
from app.models.technology_area import TechnologyArea
from app.models.organization_information import OrganizationInformation
from app.schemas.research_profile import (
    ResearchProfileCreate,
    ResearchProfileUpdate,
    ResearchDomainCreate,
    ResearchKeywordCreate,
    TechnologyAreaCreate,
    OrganizationInformationCreate,
    OrganizationInformationUpdate,
    PublicationCreate,
    PublicationUpdate,
    PatentCreate,
    PatentUpdate,
)


router = APIRouter(
    prefix="/research-profiles",
    tags=["Research Profiles"]
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_research_profile(
    profile_data: ResearchProfileCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    existing_profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Research profile already exists"
        )

    profile = ResearchProfile(
        user_id=current_user.id,
        bio=profile_data.bio,
        highest_qualification=profile_data.highest_qualification,
        current_position=profile_data.current_position,
        organization_name=profile_data.organization_name,
        orcid_id=profile_data.orcid_id
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "message": "Research profile created successfully",
        "profile_id": profile.id,
        "user_id": profile.user_id
    }


@router.get("/me")
def get_my_research_profile(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "bio": profile.bio,
        "highest_qualification": profile.highest_qualification,
        "current_position": profile.current_position,
        "organization_name": profile.organization_name,
        "orcid_id": profile.orcid_id,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }


@router.patch("/me")
def update_my_research_profile(
    profile_data: ResearchProfileUpdate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return {
        "message": "Research profile updated successfully",
        "profile_id": profile.id,
        "updated_fields": list(update_data.keys())
    }


@router.post("/me/domains", status_code=status.HTTP_201_CREATED)
def add_research_domain(
    domain_data: ResearchDomainCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    domain_name = domain_data.name.strip()

    existing_domain = db.scalar(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id,
            ResearchDomain.name == domain_name
        )
    )

    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Research domain already exists"
        )

    domain = ResearchDomain(
        research_profile_id=profile.id,
        name=domain_name
    )

    db.add(domain)
    db.commit()
    db.refresh(domain)

    return {
        "message": "Research domain added successfully",
        "domain_id": domain.id,
        "research_profile_id": domain.research_profile_id,
        "name": domain.name
    }


@router.get("/me/domains")
def get_my_research_domains(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id
        ).order_by(ResearchDomain.id)
    ).all()

    return {
        "research_profile_id": profile.id,
        "domains": [
            {
                "id": domain.id,
                "name": domain.name
            }
            for domain in domains
        ]
    }


@router.delete("/me/domains/{domain_id}")
def delete_my_research_domain(
    domain_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    domain = db.scalar(
        select(ResearchDomain).where(
            ResearchDomain.id == domain_id,
            ResearchDomain.research_profile_id == profile.id
        )
    )

    if domain is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research domain not found"
        )

    deleted_name = domain.name

    db.delete(domain)
    db.commit()

    return {
        "message": "Research domain deleted successfully",
        "deleted_domain": deleted_name
    }


@router.post("/me/keywords", status_code=status.HTTP_201_CREATED)
def add_research_keyword(
    keyword_data: ResearchKeywordCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    keyword_name = keyword_data.name.strip()

    existing_keyword = db.scalar(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id,
            ResearchKeyword.name == keyword_name
        )
    )

    if existing_keyword:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Research keyword already exists"
        )

    keyword = ResearchKeyword(
        research_profile_id=profile.id,
        name=keyword_name
    )

    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    return {
        "message": "Research keyword added successfully",
        "keyword_id": keyword.id,
        "research_profile_id": keyword.research_profile_id,
        "name": keyword.name
    }


@router.get("/me/keywords")
def get_my_research_keywords(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id
        ).order_by(ResearchKeyword.id)
    ).all()

    return {
        "research_profile_id": profile.id,
        "keywords": [
            {
                "id": keyword.id,
                "name": keyword.name
            }
            for keyword in keywords
        ]
    }

@router.post(
    "/me/technology-areas",
    status_code=status.HTTP_201_CREATED
)
def add_technology_area(
    area_data: TechnologyAreaCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    area_name = area_data.name.strip()

    existing_area = db.scalar(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id,
            TechnologyArea.name == area_name
        )
    )

    if existing_area:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Technology area already exists"
        )

    area = TechnologyArea(
        research_profile_id=profile.id,
        name=area_name
    )

    db.add(area)
    db.commit()
    db.refresh(area)

    return {
        "message": "Technology area added successfully",
        "technology_area_id": area.id,
        "research_profile_id": area.research_profile_id,
        "name": area.name
    }


@router.get("/me/technology-areas")
def get_my_technology_areas(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    areas = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        ).order_by(TechnologyArea.id)
    ).all()

    return {
        "research_profile_id": profile.id,
        "technology_areas": [
            {
                "id": area.id,
                "name": area.name
            }
            for area in areas
        ]
    }


@router.post(
    "/me/organization",
    status_code=status.HTTP_201_CREATED
)
def create_organization_information(
    organization_data: OrganizationInformationCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    existing_info = db.scalar(
        select(OrganizationInformation).where(
            OrganizationInformation.research_profile_id == profile.id
        )
    )

    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization information already exists"
        )

    organization = OrganizationInformation(
        research_profile_id=profile.id,
        **organization_data.model_dump()
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return {
        "message": "Organization information created successfully",
        "organization_information_id": organization.id
    }


@router.get("/me/organization")
def get_my_organization_information(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    organization = db.scalar(
        select(OrganizationInformation).where(
            OrganizationInformation.research_profile_id == profile.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization information not found"
        )

    return {
        "id": organization.id,
        "research_profile_id": organization.research_profile_id,
        "department": organization.department,
        "organization_type": organization.organization_type,
        "city": organization.city,
        "state": organization.state,
        "country": organization.country,
        "website": organization.website,
        "description": organization.description,
        "created_at": organization.created_at,
        "updated_at": organization.updated_at
    }


@router.patch("/me/organization")
def update_my_organization_information(
    organization_data: OrganizationInformationUpdate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    organization = db.scalar(
        select(OrganizationInformation).where(
            OrganizationInformation.research_profile_id == profile.id
        )
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization information not found"
        )

    update_data = organization_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(organization, field, value)

    db.commit()
    db.refresh(organization)

    return {
        "message": "Organization information updated successfully",
        "updated_fields": list(update_data.keys())
    }



@router.post(
    "/me/publications",
    status_code=status.HTTP_201_CREATED
)
def create_publication(
    publication_data: PublicationCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    if publication_data.doi:
        existing_publication = db.scalar(
            select(Publication).where(
                Publication.doi == publication_data.doi
            )
        )

        if existing_publication:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Publication with this DOI already exists"
            )

    publication = Publication(
        research_profile_id=profile.id,
        **publication_data.model_dump()
    )

    db.add(publication)
    db.commit()
    db.refresh(publication)

    return {
        "message": "Publication created successfully",
        "publication_id": publication.id,
        "research_profile_id": publication.research_profile_id,
        "title": publication.title
    }


@router.get("/me/publications")
def get_my_publications(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id == profile.id
        ).order_by(Publication.id)
    ).all()

    return {
        "research_profile_id": profile.id,
        "publications": [
            {
                "id": publication.id,
                "title": publication.title,
                "publication_type": publication.publication_type,
                "authors": publication.authors,
                "journal_or_conference": publication.journal_or_conference,
                "publisher": publication.publisher,
                "publication_date": publication.publication_date,
                "doi": publication.doi,
                "url": publication.url,
                "abstract": publication.abstract
            }
            for publication in publications
        ]
    }

@router.patch("/me/publications/{publication_id}")
def update_my_publication(
    publication_id: int,
    publication_data: PublicationUpdate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )

    update_data = publication_data.model_dump(
        exclude_unset=True
    )

    if "doi" in update_data and update_data["doi"]:
        existing_publication = db.scalar(
            select(Publication).where(
                Publication.doi == update_data["doi"],
                Publication.id != publication.id
            )
        )

        if existing_publication:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Publication with this DOI already exists"
            )

    for field, value in update_data.items():
        setattr(publication, field, value)

    db.commit()
    db.refresh(publication)

    return {
        "message": "Publication updated successfully",
        "publication_id": publication.id,
        "updated_fields": list(update_data.keys())
    }


@router.delete("/me/publications/{publication_id}")
def delete_my_publication(
    publication_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )

    deleted_title = publication.title

    db.delete(publication)
    db.commit()

    return {
        "message": "Publication deleted successfully",
        "deleted_publication": deleted_title
    }


@router.post(
    "/me/patents",
    status_code=status.HTTP_201_CREATED
)
def create_patent(
    patent_data: PatentCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    if patent_data.patent_number:
        existing_patent = db.scalar(
            select(Patent).where(
                Patent.patent_number == patent_data.patent_number
            )
        )

        if existing_patent:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patent with this patent number already exists"
            )

    patent = Patent(
        research_profile_id=profile.id,
        **patent_data.model_dump()
    )

    db.add(patent)
    db.commit()
    db.refresh(patent)

    return {
        "message": "Patent created successfully",
        "patent_id": patent.id,
        "research_profile_id": patent.research_profile_id,
        "title": patent.title
    }


@router.get("/me/patents")
def get_my_patents(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    patents = db.scalars(
        select(Patent).where(
            Patent.research_profile_id == profile.id
        ).order_by(Patent.id)
    ).all()

    return {
        "research_profile_id": profile.id,
        "patents": [
            {
                "id": patent.id,
                "title": patent.title,
                "patent_number": patent.patent_number,
                "inventors": patent.inventors,
                "patent_office": patent.patent_office,
                "filing_date": patent.filing_date,
                "grant_date": patent.grant_date,
                "status": patent.status,
                "url": patent.url,
                "description": patent.description
            }
            for patent in patents
        ]
    }

@router.patch("/me/patents/{patent_id}")
def update_my_patent(
    patent_id: int,
    patent_data: PatentUpdate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    patent = db.scalar(
        select(Patent).where(
            Patent.id == patent_id,
            Patent.research_profile_id == profile.id
        )
    )

    if patent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )

    update_data = patent_data.model_dump(
        exclude_unset=True
    )

    if (
        "patent_number" in update_data
        and update_data["patent_number"]
    ):
        existing_patent = db.scalar(
            select(Patent).where(
                Patent.patent_number
                == update_data["patent_number"],
                Patent.id != patent.id
            )
        )

        if existing_patent:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patent with this patent number already exists"
            )

    for field, value in update_data.items():
        setattr(patent, field, value)

    db.commit()
    db.refresh(patent)

    return {
        "message": "Patent updated successfully",
        "patent_id": patent.id,
        "updated_fields": list(update_data.keys())
    }

@router.delete("/me/patents/{patent_id}")
def delete_my_patent(
    patent_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    patent = db.scalar(
        select(Patent).where(
            Patent.id == patent_id,
            Patent.research_profile_id == profile.id
        )
    )

    if patent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patent not found"
        )

    deleted_title = patent.title

    db.delete(patent)
    db.commit()

    return {
        "message": "Patent deleted successfully",
        "deleted_patent": deleted_title
    }