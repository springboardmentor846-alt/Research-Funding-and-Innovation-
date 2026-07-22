from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    require_role,
)

from app.models.user import User

from app.services.patent_landscape_service import (
    patent_landscape,
)


router = APIRouter(

    prefix="/patent-landscape",

    tags=[
        "Global Patent Landscape"
    ]

)


@router.get("")
def global_patent_landscape(

    query: str = Query(

        ...,

        min_length=2,

        description="Technology or keyword"

    ),

    current_user: User = Depends(

        require_role(
            "researcher"
        )

    ),

    db: Session = Depends(
        get_db
    )

):

    return patent_landscape(

        query=query,

        db=db,

        current_user=current_user

    )