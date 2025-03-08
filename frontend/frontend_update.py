"""
Contain all the important things that can get changed from the frontend
"""

from llm.chat import Chat 
from interview_master.task import Task

class FrontendUpdate:
    def __init__(self, chat: Chat, code: str, code_output: str, current_task: Task):
        self.chat = chat
        self.code = code
        self.code_output = code_output
        self.current_task = current_task

    def __str__(self):
        return f"Chat: {self.chat}, Code: {self.code}, Code Output: {self.code_output}, Current Task: {self.current_task}"