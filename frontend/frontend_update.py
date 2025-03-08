"""
Contain all the important things that can get changed from the frontend
"""

from llm.chat import Chat 

class FrontendUpdate:
    def __init__(self, chat: Chat, code: str, code_output: str):
        self.chat = chat
        self.code = code
        self.code_output = code_output