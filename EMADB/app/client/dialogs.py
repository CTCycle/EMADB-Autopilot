from __future__ import annotations

import gradio as gr


###############################################################################
class SaveConfigDialog:
    def build(self) -> tuple[gr.Group, gr.Textbox, gr.Button, gr.Button]:
        with gr.Group(visible=False, elem_classes=["modal-overlay"]) as dialog:
            with gr.Column(elem_classes=["modal-content"]):
                gr.Markdown("### Save Configuration As")
                name_input = gr.Textbox(label="Enter a name for your configuration:")
                with gr.Row():
                    confirm = gr.Button("Save", variant="primary")
                    cancel = gr.Button("Cancel")
        return dialog, name_input, confirm, cancel


###############################################################################
class LoadConfigDialog:
    def build(self) -> tuple[gr.Group, gr.Dropdown, gr.Button, gr.Button]:
        with gr.Group(visible=False, elem_classes=["modal-overlay"]) as dialog:
            with gr.Column(elem_classes=["modal-content"]):
                gr.Markdown("### Load Configuration")
                dropdown = gr.Dropdown(label="Select a configuration:", choices=[], allow_custom_value=False)
                with gr.Row():
                    confirm = gr.Button("Load", variant="primary")
                    cancel = gr.Button("Cancel")
        return dialog, dropdown, confirm, cancel
