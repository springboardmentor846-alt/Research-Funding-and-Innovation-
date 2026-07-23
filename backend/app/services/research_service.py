from app.models.research_project import ResearchProject


def create_research(
    db,
    research_data,
    user_id
):
    research = ResearchProject(
        title=research_data.title,
        description=research_data.description,
        domain=research_data.domain,
        created_by=user_id
    )

    db.add(research)
    db.commit()
    db.refresh(research)

    return research


def get_all_research(db):
    return db.query(
        ResearchProject
    ).all()


def get_research_by_id(
    db,
    project_id
):
    return (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id
        )
        .first()
    )


def update_research(
    db,
    project_id,
    research_data
):
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id
        )
        .first()
    )

    if not project:
        return None

    project.title = research_data.title
    project.description = research_data.description
    project.domain = research_data.domain

    db.commit()
    db.refresh(project)

    return project
def delete_research(
    db,
    project_id
):
    project = (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id
        )
        .first()
    )

    if not project:
        return None

    db.delete(project)
    db.commit()

    return True