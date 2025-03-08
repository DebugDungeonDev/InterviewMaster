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
        "video":  """
    <video id="digital_human" 
           autoplay 
           muted 
           controls 
           style="width: 100%; height: auto; border-radius: 10px;">
        <source src="http://localhost:5000/combined_feed?nocache=1" type="video/mp4">
    </video>
    """
    }
    state = gr.State(initial_state)

    # Look in the scenarios folder and get all YAML files
    scenarios_path = "scenarios"
    scenario_files = glob.glob(os.path.join(scenarios_path, "*.yaml"))

    # Create dictionary of scenario names and their paths
    scenario_names = {}
    for scenario_file in scenario_files:
        with open(scenario_file, "r") as f:
            scenario_data = yaml.safe_load(f)
            scenario_names[scenario_data["name"]] = scenario_file

    gr.Markdown("# InterviewMaster")
    
    # Left Column - Wider IDE + task display
    with gr.Row():
        with gr.Column(scale=2):  # Left column for IDE, tasks, and buttons
            # Scenario dropdown and load button
            with gr.Row(equal_height=True):
                scenario_dropdown = gr.Dropdown(
                    [scenario_name for scenario_name in scenario_names.keys()],
                    label="Select Scenario",
                    value=list(scenario_names.keys())[0],
                    interactive=True,
                    type="value",
                    scale=5
                )
                load_button = gr.Button("Load Scenario", scale=1)

            # Task display
            task_display = gr.Markdown(label="Task Display", value=state.value['current_task'], container=True, show_label=True)

            # Code editor
            code_box = gr.Code(
                value=state.value["code"],
                language="python",
                interactive=True,
                label="Code Editor",
                lines=10,
                max_lines=25,
            )

            # Buttons
            with gr.Row():
                save_btn = gr.Button("Save", size="small")
                run_btn = gr.Button("Run", size="small")
                submit_btn = gr.Button("Submit", size="small")

            # Output box
            output_box = gr.Code(
                value=state.value["code_output"],
                language="python",
                label="Code Output",
                lines=2
            )

        # Right Column - Digital Human and Chat
        with gr.Column(scale=1):  # Digital Human and Chatbot should be in a separate column
            # Digital Human Stream
            # digital_human = gr.HTML(
            # value="""
            # <img id="video_stream" src="http://localhost:5000/video_feed" 
            #     style="width: 100%; height: auto; border-radius: 10px;">

            # <audio id="audio_stream" autoplay muted controls style="width: 100%;">
            #     <source src="http://localhost:5000/audio_feed" type="audio/mp3">
            #     </audio>
            # """,
            # label="Digital Human Live Stream"
            # )

            digital_human = gr.HTML(
            value=state.value["video"],
            label="Digital Human Live Stream"
        )

            # Chatbot area below Digital Human
            with gr.Row():
                history = state.value["chat"].to_history()
                chatbot = gr.Chatbot(history, type="messages", label="AI Chat Response", height=245)

            # User input area
            with gr.Row():
                user_input = gr.Textbox(label="Message to Bot:", placeholder="Type here...", scale=4)
                user_input.submit(fn=handle_chat, inputs=[user_input, state],
                                outputs=[code_box, output_box, task_display, chatbot, state, user_input])


    # Button click functions
    save_btn.click(fn=save_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    run_btn.click(fn=run_the_code, inputs=[code_box, state], outputs=[state, code_box, output_box])
    submit_btn.click(fn=submit_code, inputs=[code_box, state], outputs=[code_box, output_box, task_display, chatbot, state])
    load_button.click(fn=update_selected_scenario, inputs=[scenario_dropdown, state], outputs=[code_box, output_box, task_display, chatbot, state, digital_human])
demo.launch()

