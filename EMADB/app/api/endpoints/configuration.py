from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from EMADB.app.api.schemas.configuration import (
    ConfigurationListResponse,
    ConfigurationResponse,
    LoadConfigRequest,
    MessageResponse,
    SaveConfigRequest,
    UpdateConfigRequest,
)
from EMADB.app.dependencies import get_config_service
from EMADB.app.utils.services.config_service import ConfigurationService


router = APIRouter(prefix="/configuration", tags=["configuration"])


# -----------------------------------------------------------------------------
@router.get("/", response_model=ConfigurationResponse)
def read_configuration(
    service: ConfigurationService = Depends(get_config_service),
) -> ConfigurationResponse:
    configuration = service.get_configuration()
    return ConfigurationResponse(**configuration)


# -----------------------------------------------------------------------------
@router.put("/", response_model=ConfigurationResponse)
def update_configuration(
    payload: UpdateConfigRequest,
    service: ConfigurationService = Depends(get_config_service),
) -> ConfigurationResponse:
    if payload.key not in {"headless", "ignore_SSL", "wait_time", "text_drug_inputs"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid configuration key")
    updated = service.update_value(payload.key, payload.value)
    return ConfigurationResponse(**updated)


# -----------------------------------------------------------------------------
@router.post("/save", response_model=MessageResponse)
def save_configuration(
    payload: SaveConfigRequest,
    service: ConfigurationService = Depends(get_config_service),
) -> MessageResponse:
    saved_name = service.save(payload.name)
    return MessageResponse(message=f"Configuration [{saved_name}] has been saved")


# -----------------------------------------------------------------------------
@router.post("/load", response_model=ConfigurationResponse)
def load_configuration(
    payload: LoadConfigRequest,
    service: ConfigurationService = Depends(get_config_service),
) -> ConfigurationResponse:
    available = service.available_configurations()
    if payload.name not in available:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    loaded = service.load(payload.name)
    return ConfigurationResponse(**loaded)


# -----------------------------------------------------------------------------
@router.get("/available", response_model=ConfigurationListResponse)
def list_configurations(
    service: ConfigurationService = Depends(get_config_service),
) -> ConfigurationListResponse:
    files = service.available_configurations()
    return ConfigurationListResponse(files=files)
