from code_editor import code_editor
import streamlit as st
import json
from frontend import frontend_update
from llm.chat import Chat
from frontend.run_code import run_code

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
# read btns.json and info.json as custom_btns and info_bar


with open('frontend/btns.json', 'r') as f:
    custom_btns = json.load(f)

with open('frontend/info.json', 'r') as f:
    info_bar = json.load(f)

if 'current_state' not in st.session_state:
    st.session_state.current_state = frontend_update.FrontendUpdate(chat=Chat(), code="", code_output="",
                                                                        current_task=None)

col1, col2 = st.columns(2)

props = {
    "width": "px",
    "onchange": "function()",
}
# do an st.session_state to make a current state object



with col1:
    response_dict = code_editor(code=st.session_state.current_state.code, lang="python", info=info_bar, buttons=custom_btns, height=[15,20], props=props, key=0)
    st.markdown("##### Code Output")
    print(json.dumps(response_dict, indent=4))
    if response_dict['type'] == 'saved':
        st.session_state.current_state.code = response_dict['text']
    if response_dict['type'] == 'ran':
        st.session_state.current_state.code = response_dict['text']
        st.session_state.current_state.code_output = run_code(response_dict['text'])

    if response_dict['type'] == 'submit':
        st.session_state.current_state.code = response_dict['text']
        st.session_state.current_state.code_output = run_code(response_dict['text'])
        st.session_state.current_state.code = "gangalng"

    st.code(st.session_state.current_state.code_output, language='python')

