
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
        Returns the Completed or not (bool) and the reason (str).
        """
        vars = self.to_dict()
        vars["code"] = code
        vars["output"] = output
        response = self.llm.get_response_prompt_file(
            "interview_master/prompts/code_task_complete.md",
            vars,
        )

        return response  # Dict{"completed": bool, "reason": str}
    
    def check_question_complete(self, chat: Chat):
        """
        Checks if the question is correct.
        Returns the Completed or not (bool) and the reason (str).
        """
        vars = self.to_dict
        vars["last_chat_response"] = chat.messages[-1].message

        assert chat.messages[-1].isHuman, "Last message should be from the user."

        response = self.llm.get_response_prompt_file(
            "interview_master/prompts/question_task_complete.md",
            vars,
        )

        return response # Dict{"completed": bool, "reason": str}


    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "success_description": self.success_description,
        }
        


        