import io
import sys

import gradio as gr
import json
from llm.chat import Chat
from frontend import frontend_update
from frontend.utils.button_functions import save_code, run_the_code, submit_code, handle_chat

# Build the Gradio interface
with gr.Blocks() as demo:
    initial_state = {
        "code": "",
        "code_output": "",
        "chat": Chat(),
        "current_task": "Your current task will appear here."
    }
    state = gr.State(initial_state)

    gr.Markdown("# Debug Dungeon")

    with gr.Row():
        # Left Column - Code Editor
        with gr.Column(scale=1):
            gr.Dropdown()
            code_box = gr.Code(
                value=state.value["code"],
                language="python",
                interactive=True,
                label="Code Editor",
                lines=10,
                max_lines=25,
            )


            with gr.Row():
                save_btn = gr.Button("Save", size="small")
                run_btn = gr.Button("Run", size="small")
                submit_btn = gr.Button("Submit", size="small")

            output_box = gr.Code(
                value=state.value["code_output"],
                language="python",
                label="Code Output",
                lines=5
            )


        # Right Column - Split into 3 areas
        with gr.Column(scale=1):
            # Top Half - Split into two
            with gr.Row():
                task_display = gr.Textbox(
                    value=state.value['current_task'],
                    label="Task",
                    interactive=False,
                    scale=1,  # Control width, not height
                    lines=5  # Increase the height by increasing the number of lines
                )
                digital_human = gr.Markdown(
                    "_[NVIDIA Digital Human Placeholder]_",
                )

            # Bottom Half - Chat Field
            with gr.Row():
                history = state.value["chat"].to_history()
                chatbot = gr.Chatbot(history, type="messages", label="AI Chat Response", height=245)  # Adjust the height as needed
            with gr.Row():

            # Textbox for user input
                user_input = gr.Textbox(label="Type your message (make sure to save before sending a chat!):", placeholder="Type here...", scale=4)

                # Send button to trigger response
                send_button = gr.Button("Send",scale=1)

    # Button click functions
    save_btn.click(fn=save_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    run_btn.click(fn=run_the_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    submit_btn.click(fn=submit_code, inputs=[code_box, state], outputs=[state, code_box, output_box, chatbot])
    send_button.click(fn=handle_chat, inputs=[user_input, state],outputs=[chatbot, user_input, state]
    )

demo.launch()
