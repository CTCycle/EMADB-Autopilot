from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI

from EMADB.app.logger import logger


###############################################################################
class UIController:
    def __init__(self, fastapi_app: FastAPI) -> None:
        self.app = fastapi_app
        self.base_url = "http://test"
        self.timeout = httpx.Timeout(30.0)

    # -------------------------------------------------------------------------
    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async with httpx.AsyncClient(app=self.app, base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    # -------------------------------------------------------------------------
    async def get_configuration(self) -> dict[str, Any]:
        try:
            response = await self._request("GET", "/api/configuration/")
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to fetch configuration: {exc}")
            return {}

    # -------------------------------------------------------------------------
    async def update_configuration(self, key: str, value: Any) -> dict[str, Any]:
        try:
            response = await self._request(
                "PUT",
                "/api/configuration/",
                json={"key": key, "value": value},
            )
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to update configuration [{key}]: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def save_configuration(self, name: str) -> str:
        try:
            response = await self._request(
                "POST",
                "/api/configuration/save",
                json={"name": name},
            )
            return response.json()["message"]
        except httpx.HTTPError as exc:
            logger.error(f"Failed to save configuration: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def load_configuration(self, name: str) -> dict[str, Any]:
        try:
            response = await self._request(
                "POST",
                "/api/configuration/load",
                json={"name": name},
            )
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to load configuration [{name}]: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def list_configurations(self) -> list[str]:
        try:
            response = await self._request("GET", "/api/configuration/available")
            return response.json()["files"]
        except httpx.HTTPError as exc:
            logger.error(f"Failed to list configurations: {exc}")
            return []

    # -------------------------------------------------------------------------
    async def search_from_file(self) -> dict[str, Any]:
        try:
            response = await self._request("POST", "/api/search/file")
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to start file search: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def search_from_text(self, query: str) -> dict[str, Any]:
        try:
            response = await self._request(
                "POST",
                "/api/search/text",
                json={"query": query},
            )
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to start text search: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def stop_task(self, task_id: str) -> dict[str, Any]:
        try:
            response = await self._request(
                "POST",
                "/api/search/stop",
                json={"task_id": task_id},
            )
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to stop task [{task_id}]: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def task_status(self, task_id: str) -> dict[str, Any]:
        try:
            response = await self._request("GET", f"/api/search/{task_id}")
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to fetch task status [{task_id}]: {exc}")
            raise

    # -------------------------------------------------------------------------
    async def check_driver(self) -> dict[str, str]:
        try:
            response = await self._request("GET", "/api/search/check/driver")
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Failed to check driver installation: {exc}")
            raise
