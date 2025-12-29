from pydantic import BaseModel, Field
from typing import Optional


class ImageSummary(BaseModel):
    """Summary of a Docker image."""

    id: str = Field(..., description="Image ID")
    tags: list[str] = Field(default_factory=list, description="Image tags")
    size: int = Field(0, description="Image size in bytes")
    created: int = Field(0, description="Creation timestamp")


class ImageListResponse(BaseModel):
    """Response for image list endpoint."""

    images: list[ImageSummary]
    total: int

