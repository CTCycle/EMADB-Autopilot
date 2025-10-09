from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


###############################################################################
class ConfigurationResponse(BaseModel):
    headless: bool = Field(...)
    ignore_SSL: bool = Field(...)
    wait_time: float = Field(...)
    text_drug_inputs: str = Field("")


###############################################################################
class UpdateConfigRequest(BaseModel):
    key: str
    value: Any


###############################################################################
class SaveConfigRequest(BaseModel):
    name: str


###############################################################################
class LoadConfigRequest(BaseModel):
    name: str


###############################################################################
class ConfigurationListResponse(BaseModel):
    files: list[str]


###############################################################################
class MessageResponse(BaseModel):
    message: str
