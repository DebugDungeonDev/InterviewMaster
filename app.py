import gradio as gr
import json

# If you have these modules available just like in your Streamlit setup:
# from frontend.run_code import run_code
# from frontend import frontend_update
# from llm.chat import Chat

# For demonstration, let's define a simple run_code placeholder.
def run_code(code_str):
    """
    Replace this with your actual run_code function that executes
    the code and returns output.
    """
    # Example stub:
    return f"Executed:\n{code_str}"

# Load your JSON files
with open("frontend/btns.json", "r") as f:
    custom_btns = json.load(f)

with open("frontend/info.json", "r") as f:
    info_bar = json.load(f)

# -----------------------------------------------------------------------------------
# Gradio App
# -----------------------------------------------------------------------------------

# Each button will call one of these functions to mimic the Streamlit behavior
def save_code(code, state):
    """
    Mimic 'saved' in Streamlit:
    - Just store the code in the state.
    """
    state["code"] = code
    return state, state["code"], state["code_output"]

def run_the_code(code, state):
    """
    Mimic 'ran':
    - Store code in state
    - Execute code and store its output
    """
    state["code"] = code
    state["code_output"] = run_code(code)
    return state, state["code"], state["code_output"]

def submit_code(code, state):
    """
    Mimic 'submit':
    - Execute code and store its output
    - Then set the code to 'gangalng'
    """
    state["code"] = code
    state["code_output"] = run_code(code)
    state["code"] = "gangalng"
    return state, state["code"], state["code_output"]

# Build the Gradio interface
with gr.Blocks() as demo:
    # We replicate your "session" with a dictionary in gr.State
    initial_state = {
        "code": "",
        "code_output": "",
        # "chat": Chat(),  # If you have Chat object from llm.chat
        # "current_task": None
    }
    state = gr.State(initial_state)

    gr.Markdown("## Code Editor Demo (Converted from Streamlit)")

    with gr.Row():
        with gr.Column():
            code_box = gr.Code(
                value=initial_state["code"], 
                language="python", 
                interactive=True, 
                label="Code Editor"
            )

            # Buttons to mimic 'saved', 'ran', and 'submit'
            save_btn = gr.Button("Save")
            run_btn = gr.Button("Run")
            submit_btn = gr.Button("Submit")

            # Output area (like `st.code(..., language='python')`)
            output_box = gr.Code(
                value=initial_state["code_output"], 
                language="python", 
                label="Code Output"
            )

        # Second column, left empty for now (matches your col2)
        with gr.Column():
            gr.Markdown("_(Empty column)_")

    # Button click => update state, code_box, and output_box
    save_btn.click(
        fn=save_code, 
        inputs=[code_box, state], 
        outputs=[state, code_box, output_box]
    )

    run_btn.click(
        fn=run_the_code, 
        inputs=[code_box, state], 
        outputs=[state, code_box, output_box]
    )

    submit_btn.click(
        fn=submit_code, 
        inputs=[code_box, state], 
        outputs=[state, code_box, output_box]
    )

demo.launch()
