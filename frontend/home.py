from code_editor import code_editor
import streamlit as st
import json

# read btns.json and info.json as custom_btns and info_bar

with open('frontend/btns.json', 'r') as f:
    custom_btns = json.load(f)

with open('frontend/info.json', 'r') as f:
    info_bar = json.load(f)


response_dict = code_editor("", lang="python", info=info_bar, buttons=custom_btns, height=[10,20], key='main')

if(response_dict['type'] == 'submit'):
    st.code(response_dict['text'], language=response_dict['lang'])