from typing import List
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, field_validator
    
class SingleFileUploadSchema(BaseModel):
    path: str
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        path: str = Form(...),
        file: UploadFile = File(...),
    ):
        return cls(path=path, file=file)



class MultipleFileUploadSchema(BaseModel):
    """
    Generic file upload schema for all modules
    """

    path: str = Field(..., description="Upload directory path (e.g. banners, users/profile)")
    files: List[UploadFile] = File(..., description="Files to upload")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Path cannot be empty")
        return v

    @field_validator("files")
    @classmethod
    def validate_files(cls, files: List[UploadFile]):
        if not files:
            raise ValueError("At least one file is required")
        return files

    @classmethod
    def as_form(
        cls,
        path: str = Form(...),
        files: List[UploadFile] = File(...),
    ):
        return cls(path=path, files=files)
