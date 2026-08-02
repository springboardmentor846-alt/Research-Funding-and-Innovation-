import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException

# Base uploads directory
UPLOAD_DIR = "uploads"

# Maximum file size (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "csv",
    "zip",
    "png",
    "jpg",
    "jpeg",
}

# Folder mapping
DOCUMENT_FOLDER_MAP = {
    "Research Paper": "research_papers",
    "Patent": "patents",
    "Prototype": "prototypes",
    "Document": "documents",
    "Image": "images",
    "Dataset": "datasets",
}


def validate_file(file: UploadFile):
    """
    Validate uploaded file extension.
    """

    extension = file.filename.split(".")[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{extension}' is not allowed."
        )

    return extension


def save_file(file: UploadFile, document_type: str):
    """
    Save uploaded file to disk.
    """

    extension = validate_file(file)

    folder = DOCUMENT_FOLDER_MAP.get(document_type)

    if not folder:
        raise HTTPException(
            status_code=400,
            detail="Invalid document type."
        )

    os.makedirs(os.path.join(UPLOAD_DIR, folder), exist_ok=True)

    unique_filename = f"{uuid.uuid4()}.{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        folder,
        unique_filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail="File size exceeds 50 MB."
        )

    return {
        "original_filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": file_path,
        "file_extension": extension,
        "file_size": file_size,
        "mime_type": file.content_type,
    }


def delete_file(file_path: str):
    """
    Delete file from disk.
    """

    if os.path.exists(file_path):
        os.remove(file_path)