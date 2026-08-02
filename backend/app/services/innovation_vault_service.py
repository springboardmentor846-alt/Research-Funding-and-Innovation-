from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models.innovation_vault import InnovationVault
from app.models.innovation_portfolio import InnovationPortfolio

from app.schemas.innovation_vault_schema import (
    InnovationVaultCreate,
    InnovationVaultUpdate,
)

from app.utils.file_handler import (
    save_file,
    delete_file as remove_file_from_disk,
)
def upload_file(
    db: Session,
    file: UploadFile,
    vault_data: InnovationVaultCreate,
    current_user: dict,
):
    # Check portfolio ownership
    portfolio = (
        db.query(InnovationPortfolio)
        .filter(
            InnovationPortfolio.id == vault_data.portfolio_id,
            InnovationPortfolio.user_id == current_user["id"],
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found."
        )

    # Save file to disk
    file_info = save_file(
        file=file,
        document_type=vault_data.document_type.value,
    )

    vault = InnovationVault(
        user_id=current_user["id"],
        portfolio_id=vault_data.portfolio_id,
        title=vault_data.title,
        description=vault_data.description,
        document_type=vault_data.document_type,

        original_filename=file_info["original_filename"],
        stored_filename=file_info["stored_filename"],
        file_path=file_info["file_path"],
        file_extension=file_info["file_extension"],
        file_size=file_info["file_size"],
        mime_type=file_info["mime_type"],

        visibility=vault_data.visibility,
        nda_required=vault_data.nda_required,
    )

    db.add(vault)
    db.commit()
    db.refresh(vault)

    return vault
def get_all_files(
    db: Session,
    current_user: dict,
):
    files = (
        db.query(InnovationVault)
        .filter(
            InnovationVault.user_id == current_user["id"]
        )
        .order_by(
            InnovationVault.uploaded_at.desc()
        )
        .all()
    )

    return files
def get_file_by_id(
    vault_id: int,
    db: Session,
    current_user: dict,
):
    vault = (
        db.query(InnovationVault)
        .filter(
            InnovationVault.id == vault_id,
            InnovationVault.user_id == current_user["id"],
        )
        .first()
    )

    if not vault:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return vault
def update_file_metadata(
    vault_id: int,
    vault_data: InnovationVaultUpdate,
    db: Session,
    current_user: dict,
):
    vault = (
        db.query(InnovationVault)
        .filter(
            InnovationVault.id == vault_id,
            InnovationVault.user_id == current_user["id"],
        )
        .first()
    )

    if not vault:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    update_data = vault_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vault, key, value)

    db.commit()
    db.refresh(vault)

    return vault
def delete_file_record(
    vault_id: int,
    db: Session,
    current_user: dict,
):
    vault = (
        db.query(InnovationVault)
        .filter(
            InnovationVault.id == vault_id,
            InnovationVault.user_id == current_user["id"],
        )
        .first()
    )

    if not vault:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    # Delete physical file
    remove_file_from_disk(vault.file_path)

    # Delete database record
    db.delete(vault)
    db.commit()

    return {
        "message": "File deleted successfully."
    }