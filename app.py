import io
import sys
import os
import glob

import gradio as gr
import json

import yaml

from llm.chat import Chat
from interview_master.scenario import Scenario
from interview_master.interview_master import InterviewMaster
from frontend import frontend_update
from frontend.utils.button_functions import save_code, run_the_code, submit_code, handle_chat, update_selected_scenario
from llm.clients.gemini import Gemini

# Build the Gradio interface
with gr.Blocks() as demo:
    initial_state = {
        "code": "",
        "code_output": "",
        "chat": Chat(),
        "current_task": "Your current task will appear here.",
        "scenario_name": "Calculator Application",
    }
    state = gr.State(initial_state)

    #look in the scnearios folder nad for each scneario yaml file, access its name and then keep a list of its path and its name
    scenarios_path = "scenarios"
    scenario_files = glob.glob(os.path.join(scenarios_path, "*.yaml"))

    # in the yaml files there will be a key called name, get the value of that key
    scenario_names = {}
    for scenario_file in scenario_files:
        # store it as name : path
        with open(scenario_file, "r") as f:
            scenario_data = yaml.safe_load(f)
            scenario_names[scenario_data["name"]] = scenario_file




    gr.Markdown("# Debug Dungeon")

    with gr.Row():
        # Left Column - Code Editor
        with gr.Column(scale=1):
            #dropdown with scenario names
            with gr.Row():
                scenario_dropdown = gr.Dropdown(
                    [scenario_name for scenario_name in scenario_names.keys()],
                    label="Select Scenario",
                    value=list(scenario_names.keys())[0],
                    interactive=True,
                    type="value",
                    scale=1
                )

                load_button = gr.Button("Load Scenario", scale=1)

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
                # do a placeholder text box for digital human
                # Placeholder for Digital Human

                digital_human = gr.Textbox(
                    value="Placeholder",
                    label="Digital Human",
                    interactive=False,
                    scale=1
                )
                # digital_human = gr.Video(
                #     value="couch.mp4",   # path or filename
                #     label="Digital Human",
                #     interactive=False,          # do not allow user to interact with the video
                #     autoplay=True,            # start playing automatically
                #     loop=False                # do not loop, plays only once
                # )

            # Bottom Half - Chat Field
            with gr.Row():
                history = state.value["chat"].to_history()
                chatbot = gr.Chatbot(history, type="messages", label="AI Chat Response", height=245)  # Adjust the height as needed
            with gr.Row():

            # Textbox for user input
                user_input = gr.Textbox(label="Type your message (make sure to save before sending a chat!):", placeholder="Type here...", scale=4)

                # Send button to trigger response
                send_button = gr.Button("Send",scale=1)
                user_input.submit(fn=handle_chat, inputs=[user_input, state],
                                  outputs=[code_box, output_box, task_display, chatbot, state, user_input, digital_human])

    # Button click functions
    save_btn.click(fn=save_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    run_btn.click(fn=run_the_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    submit_btn.click(fn=submit_code, inputs=[code_box, state], outputs=[code_box, output_box, task_display, chatbot, state,digital_human])
    send_button.click(fn=handle_chat, inputs=[user_input, state],outputs=[code_box, output_box, task_display, chatbot, state, user_input, digital_human])
    load_button.click(fn=update_selected_scenario, inputs=[scenario_dropdown, state], outputs=[code_box, output_box, task_display, chatbot, state,digital_human])

demo.launch()
