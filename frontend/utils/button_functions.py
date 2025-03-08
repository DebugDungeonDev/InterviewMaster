import glob
import os

import yaml

from frontend.frontend_update import FrontendUpdate
from frontend.run_code import run_code
from interview_master.interview_master import InterviewMaster
from interview_master.scenario import Scenario
from llm.chat import Message
from llm.clients.gemini import Gemini
import requests
import random 

IM: InterviewMaster = None

def update_video_feed(state):
    # Request to 
    new_path = "couch.mp4"
    requests.post("http://localhost:5000/switch_video", json={"path": new_path})

    r = random.randint(0, 1000000)

    state['video'] = f"""
    <video id="digital_human" 
           autoplay 
           muted 
           controls 
           style="width: 100%; height: auto; border-radius: 10px;">
        <source src="http://localhost:5000/combined_feed?nocache={r}" type="video/mp4">
    </video>
    """

def update_state_from_fru(state, fru):
    state["chat"] = fru.chat
    state["code"] = fru.code
    state["code_output"] = fru.code_output
    state["current_task"] = fru.current_task
    return state


def save_code(code, state):
    state["code"] = code
    return state, state["code"], state["code_output"]

def run_the_code(code, state):
    state["code"] = code
    state["code_output"] = run_code(code)
    return state, state["code"], state["code_output"]

def submit_code(code, state):
    state["code"] = code
    state["code_output"] = run_code(code)

    FRU = IM.handle_code_submission(Gemini("llm/clients/google.key"), FrontendUpdate(state["chat"], state["code"], state["code_output"], state["current_task"]))
    state = update_state_from_fru(state, FRU)

    task_details = f"### Task {IM.task_manager.previous_tasks.__len__() + 1}: **{FRU.current_task.name}**\n\n{FRU.current_task.description}"

    return state["code"], state["code_output"], task_details, state["chat"].to_history(), state


def handle_chat(user_input, state):
    global IM
    chat = state["chat"]  # Get the chat from state

    # Append user input to chat
    chat.messages.append(Message(True, user_input))  # True means it's from the human

    # Simulate an AI response (replace with your AI model here)
    FRU = IM.handle_chat_message(Gemini("llm/clients/google.key"), FrontendUpdate(chat, state["code"], state["code_output"], state["current_task"]))
    state = update_state_from_fru(state, FRU)

    task_details = f"### Task {IM.task_manager.previous_tasks.__len__() + 1}: **{FRU.current_task.name}**\n\n{FRU.current_task.description}"
    # Return updated chat history and clear user input
    return state["code"], state["code_output"], task_details, state["chat"].to_history(), state, ""


def update_selected_scenario(selected_scenario, state):
    global IM
    # Get scenario names
    #iterate through the scenarios folder until find a name that matches
    scenarios_path = "scenarios"
    scenario_files = glob.glob(os.path.join(scenarios_path, "*.yaml"))
    print("Scenario files found:", scenario_files)  # Debugging
    for scenario_file in scenario_files:
        # store it as name : path
        print("Checking scenario file:", scenario_file)
        with open(scenario_file, "r") as f:
            scenario_data = yaml.safe_load(f)
            if scenario_data["name"] == selected_scenario:
                selected_scenario_file = scenario_file
                break

    update_video_feed(state)

    state["scenario_name"] = selected_scenario  # No need for `.value`

    # Load scenario into InterviewMaster
    IM = InterviewMaster(Scenario(Gemini("llm/clients/google.key"), selected_scenario_file))
    FRU = IM.handle_start()

    task_details = f"### Task {IM.task_manager.previous_tasks.__len__() + 1}: **{FRU.current_task.name}**\n\n{FRU.current_task.description}"
    state = update_state_from_fru(state, FRU)



    return state["code"], state["code_output"], task_details, state["chat"].to_history(), state, state['video']