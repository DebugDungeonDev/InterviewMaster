import glob
import os

import yaml

from frontend.run_code import run_code
from interview_master.interview_master import InterviewMaster
from interview_master.scenario import Scenario
from llm.chat import Message
from llm.clients.gemini import Gemini


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
    # RUN AI CALL FROM ETHAN
    return state, state["code"], state["code_output"], state["chat"].to_history()


def handle_chat(user_input, state):
    chat = state["chat"]  # Get the chat from state

    # Append user input to chat
    chat.messages.append(Message(True, user_input))  # True means it's from the human

    # Simulate an AI response (replace with your AI model here)
    ai_response = f"AI Response to: {user_input}"
    chat.messages.append(Message(False, ai_response))  # False means it's from the AI

    # Update the state with the new chat
    state["chat"] = chat

    # Return updated chat history and clear user input
    return chat.to_history(), "", state


def update_selected_scenario(selected_scenario, state):
    # Get scenario names
    #iterate through the scenarios folder until find a name that matches
    scenarios_path = "scenarios"
    scenario_files = glob.glob(os.path.join(scenarios_path, "*.yaml"))
    for scenario_file in scenario_files:
        # store it as name : path
        with open(scenario_file, "r") as f:
            scenario_data = yaml.safe_load(f)
            if scenario_data["name"] == selected_scenario:
                selected_scenario_file = scenario_file
                break

    state["scenario_name"] = selected_scenario  # No need for `.value`

    # Load scenario into InterviewMaster
    IM = InterviewMaster(Scenario(Gemini("llm/clients/google.key"), selected_scenario_file))
    FRU = IM.handle_start()

    print(FRU)

    # Update state values
    state["chat"] = FRU.chat
    state["code"] = FRU.code
    state["code_output"] = FRU.code_output
    state["current_task"] = FRU.current_task

    return state["code"], state["current_task"]