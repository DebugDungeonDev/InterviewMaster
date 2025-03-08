
from llm.llm import LLM
from llm.chat import Chat, Message
from typing import List
import enum 

class TaskType(enum.Enum):
    """
    Enum for the type of task.
    """
    CODE = 1
    QUESTION = 2


class Task:
    def __init__(self, llm: LLM, task_type:TaskType, name:str, description:str, success_description:str):
        self.llm = llm
        self.task_type = task_type
        self.name = name
        self.description = description
        self.success_description = success_description

    def check_complete(self, code: str, output: str, chat: Chat):
        if self.task_type == TaskType.CODE:
            return self.check_code_complete(code, output, chat)
        elif self.task_type == TaskType.QUESTION:
            return self.check_question_complete(chat)
        else:
            return NotImplementedError
        
    def check_code_complete(self, code: str, output: str, chat: Chat):
        """
        Checks if the code is correct.
        """
        


        