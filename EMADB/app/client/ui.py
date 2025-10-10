from __future__ import annotations

from typing import Any

import gradio as gr
import httpx

from EMADB.app.client.controllers import UIController
from EMADB.app.client.dialogs import LoadConfigDialog, SaveConfigDialog
from EMADB.app.logger import logger

CUSTOM_CSS = """
#main-column {max-width: 1000px; margin: auto;}
.group-box {border: 1px solid var(--border-color-primary); padding: 1rem; border-radius: 6px; background: var(--block-background-fill);
box-shadow: 0 2px 6px rgba(0,0,0,0.1);}
.status-bar {font-weight: 600;}
.modal-overlay {position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000;}
.modal-content {background: var(--block-background-fill); padding: 1.5rem; border-radius: 8px; min-width: 320px; max-width: 480px; box-shadow: 0 10px 30px rgba(0,0,0,0.25);}
"""


###############################################################################
class UIBindings:
    def __init__(self, controller: UIController) -> None:
        self.controller = controller

    # -------------------------------------------------------------------------
    async def update_headless(self, value: bool) -> str:
        await self.controller.update_configuration("headless", value)
        return "Headless mode enabled" if value else "Headless mode disabled"

    # -------------------------------------------------------------------------
    async def update_ignore_ssl(self, value: bool) -> str:
        await self.controller.update_configuration("ignore_SSL", value)
        return "Ignoring SSL errors" if value else "SSL errors will be enforced"

    # -------------------------------------------------------------------------
    async def update_wait_time(self, value: float) -> str:
        await self.controller.update_configuration("wait_time", value)
        return f"Wait time updated to {value:.1f}s"

    # -------------------------------------------------------------------------
    async def save_configuration(self, name: str) -> tuple[str, Any]:
        try:
            message = await self.controller.save_configuration(name)
            return message, gr.update(visible=False)
        except httpx.HTTPError as exc:
            logger.error(f"Save configuration failed: {exc}")
            return "Unable to save configuration. Check logs for details.", gr.update(visible=False)

    # -------------------------------------------------------------------------
    async def open_load_dialog(self) -> tuple[Any, Any, str]:
        files = await self.controller.list_configurations()
        if not files:
            return gr.update(choices=[]), gr.update(visible=False), "No saved configurations found."
        dropdown_update = gr.update(choices=files, value=files[0])
        return dropdown_update, gr.update(visible=True), "Select a configuration to load."

    # -------------------------------------------------------------------------
    async def open_save_dialog(self) -> Any:
        return gr.update(visible=True)

    # -------------------------------------------------------------------------
    async def cancel_dialog(self) -> Any:
        return gr.update(visible=False)

    # -------------------------------------------------------------------------
    async def load_configuration(
        self,
        name: str,
    ) -> tuple[bool, bool, float, str, str, Any]:
        try:
            configuration = await self.controller.load_configuration(name)
            return (
                bool(configuration.get("headless", False)),
                bool(configuration.get("ignore_SSL", False)),
                float(configuration.get("wait_time", 5.0)),
                configuration.get("text_drug_inputs", ""),
                f"Loaded configuration [{name}]",
                gr.update(visible=False),
            )
        except httpx.HTTPError as exc:
            logger.error(f"Load configuration failed: {exc}")
            return False, False, 5.0, "", "Unable to load configuration. Check logs for details.", gr.update(visible=False)

    # -------------------------------------------------------------------------
    async def search_from_text(
        self, query: str, current_task: str
    ) -> tuple[str, str, Any]:
        try:
            response = await self.controller.search_from_text(query)
            task_id = response.get("task_id", "")
            message = response.get("message", "Search started")
            timer_state = gr.update(active=bool(task_id))
            return message, task_id, timer_state
        except httpx.HTTPError as exc:
            logger.error(f"Search from text failed: {exc}")
            return "Unable to start search. Check logs for details.", current_task, gr.update(active=False)

    # -------------------------------------------------------------------------
    async def search_from_file(self, current_task: str) -> tuple[str, str, Any]:
        try:
            response = await self.controller.search_from_file()
            task_id = response.get("task_id", "")
            message = response.get("message", "Search started")
            return message, task_id, gr.update(active=bool(task_id))
        except httpx.HTTPError as exc:
            logger.error(f"Search from file failed: {exc}")
            return "Unable to start search. Check logs for details.", current_task, gr.update(active=False)

    # -------------------------------------------------------------------------
    async def stop_task(self, task_id: str) -> tuple[str, str, Any]:
        if not task_id:
            return "No active search to stop.", task_id, gr.update(active=False)
        try:
            response = await self.controller.stop_task(task_id)
            message = response.get("message", "Interrupt requested")
            return message, "", gr.update(active=False)
        except httpx.HTTPError as exc:
            logger.error(f"Stop task failed: {exc}")
            return "Failed to stop task. Check logs for details.", task_id, gr.update(active=True)

    # -------------------------------------------------------------------------
    async def poll_task(self, task_id: str) -> tuple[str, str, Any]:
        if not task_id:
            return "Ready.", task_id, gr.update(active=False)
        try:
            status = await self.controller.task_status(task_id)
            state = status.get("status", "unknown")
            if state in {"completed", "failed", "cancelled"}:
                message = "Search completed successfully." if state == "completed" else "Search did not complete."
                if status.get("error"):
                    message += f" Error: {status['error']}"
                return message, "", gr.update(active=False)
            return f"Search in progress... ({state})", task_id, gr.update(active=True)
        except httpx.HTTPError as exc:
            logger.error(f"Polling task failed: {exc}")
            return "Unable to poll task status.", "", gr.update(active=False)

    # -------------------------------------------------------------------------
    async def check_driver(self) -> str:
        try:
            response = await self.controller.check_driver()
            return response.get("message", "Driver check completed")
        except httpx.HTTPError as exc:
            logger.error(f"Check driver failed: {exc}")
            return "Driver check failed. Check logs for details."

    # -------------------------------------------------------------------------
    def reload_notice(self) -> str:
        return "Reload the application from your browser."


###############################################################################
def build_interface(controller: UIController, initial_config: dict[str, Any]) -> gr.Blocks:
    bindings = UIBindings(controller)
    with gr.Blocks(css=CUSTOM_CSS, title="EMAutoPilot v1.0") as demo:
        status_bar = gr.Markdown("Ready.", elem_classes=["status-bar"])
        task_state = gr.State("")
        timer = gr.Timer(1.5, active=False)

        save_dialog = SaveConfigDialog()
        load_dialog = LoadConfigDialog()
        save_modal, save_name, save_confirm, save_cancel = save_dialog.build()
        load_modal, load_dropdown, load_confirm, load_cancel = load_dialog.build()

        with gr.Column(elem_id="main-column"):
            with gr.Row():
                save_button = gr.Button("Save current configuration", variant="secondary")
                load_button = gr.Button("Load configuration", variant="secondary")
                reload_button = gr.Button("Reload application", variant="secondary")
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Group(elem_classes=["group-box"]):
                        gr.HTML("""<span style='font-size: 14px;'>Insert drug names (separated by comma)</span>""")
                        drug_inputs = gr.Textbox(
                            value=initial_config.get("text_drug_inputs", ""),
                            lines=12,
                            placeholder="Drug names separated by commas",
                            show_label=False,
                        )
                        search_text = gr.Button("Search from text box", variant="primary")
                        search_file = gr.Button("Search from file")
                        stop_search = gr.Button("Stop search", variant="stop")
                with gr.Column(scale=1):
                    with gr.Group(elem_classes=["group-box"]):
                        gr.Markdown("## Configurations")
                        ignore_ssl = gr.Checkbox(
                            label="Ignore SSL errors",
                            value=bool(initial_config.get("ignore_SSL", False)),
                        )
                        headless = gr.Checkbox(
                            label="Headless mode",
                            value=bool(initial_config.get("headless", False)),
                        )
                        wait_time = gr.Number(
                            label="Wait time (s)",
                            value=float(initial_config.get("wait_time", 5.0)),
                            precision=1,
                        )
                        check_driver = gr.Button("Check webdriver installation")

        save_button.click(bindings.open_save_dialog, outputs=save_modal)
        save_confirm.click(bindings.save_configuration, inputs=save_name, outputs=[status_bar, save_modal])
        save_cancel.click(bindings.cancel_dialog, outputs=save_modal)

        load_button.click(bindings.open_load_dialog, outputs=[load_dropdown, load_modal, status_bar])
        load_confirm.click(
            bindings.load_configuration,
            inputs=load_dropdown,
            outputs=[headless, ignore_ssl, wait_time, drug_inputs, status_bar, load_modal],
        )
        load_cancel.click(bindings.cancel_dialog, outputs=load_modal)

        headless.change(bindings.update_headless, inputs=headless, outputs=status_bar)
        ignore_ssl.change(bindings.update_ignore_ssl, inputs=ignore_ssl, outputs=status_bar)
        wait_time.change(bindings.update_wait_time, inputs=wait_time, outputs=status_bar)

        search_text.click(
            bindings.search_from_text,
            inputs=[drug_inputs, task_state],
            outputs=[status_bar, task_state, timer],
        )
        search_file.click(
            bindings.search_from_file,
            inputs=task_state,
            outputs=[status_bar, task_state, timer],
        )
        stop_search.click(
            bindings.stop_task,
            inputs=task_state,
            outputs=[status_bar, task_state, timer],
        )
        check_driver.click(bindings.check_driver, outputs=status_bar)
        timer.tick(bindings.poll_task, inputs=task_state, outputs=[status_bar, task_state, timer])
        reload_button.click(bindings.reload_notice, outputs=status_bar)

    return demo
