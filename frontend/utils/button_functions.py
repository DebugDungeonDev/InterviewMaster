from frontend.run_code import run_code
from llm.chat import Message


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
    state.value["scenario_name"] = selected_scenario
    return state