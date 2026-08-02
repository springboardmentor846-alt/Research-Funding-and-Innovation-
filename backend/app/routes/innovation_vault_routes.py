print("✅ innovation_vault_routes.py loaded")
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.auth_dependency import get_current_user

from app.schemas.innovation_vault_schema import (
    InnovationVaultCreate,
    InnovationVaultUpdate,
    InnovationVaultResponse,
)

from app.services.innovation_vault_service import (
    upload_file,
    get_all_files,
    get_file_by_id,
    update_file_metadata,
    delete_file_record,
)

from app.models.innovation_vault import (
    DocumentType,
    Visibility,
)

router = APIRouter(
    prefix="/vault",
    tags=["Innovation Vault"],
)
@router.post(
    "/upload",
    response_model=InnovationVaultResponse,
)
def upload_vault_file(
    portfolio_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    document_type: DocumentType = Form(...),
    visibility: Visibility = Form(Visibility.PRIVATE),
    nda_required: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    vault_data = InnovationVaultCreate(
        portfolio_id=portfolio_id,
        title=title,
        description=description,
        document_type=document_type,
        visibility=visibility,
        nda_required=nda_required,
    )

    return upload_file(
        db=db,
        file=file,
        vault_data=vault_data,
        current_user=current_user,
    )
@router.get(
    "/files",
    response_model=list[InnovationVaultResponse],
)
def get_files(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    return get_all_files(
        db=db,
        current_user=current_user,
    )
@router.get(
    "/{vault_id}",
    response_model=InnovationVaultResponse,
)
def get_single_file(
    vault_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    return get_file_by_id(
        vault_id=vault_id,
        db=db,
        current_user=current_user,
    )
@router.put(
    "/{vault_id}",
    response_model=InnovationVaultResponse,
)
def update_file(
    vault_id: int,
    vault_data: InnovationVaultUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    return update_file_metadata(
        vault_id=vault_id,
        vault_data=vault_data,
        db=db,
        current_user=current_user,
    )
@router.delete("/{vault_id}")
def delete_file(
    vault_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    return delete_file_record(
        vault_id=vault_id,
        db=db,
        current_user=current_user,
    )