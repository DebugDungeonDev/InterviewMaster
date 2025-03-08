
from llm.llm import LLM
from llm.utils import str_to_bool
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

        self.completed = False 

    def check_complete(self, code: str = "", output: str = "", chat: Chat = None):
        response = None
        if self.task_type == TaskType.CODE:
            response = self._check_code_complete(code, output)
        elif self.task_type == TaskType.QUESTION:
            response = self._check_question_complete(chat)
        else:
            return NotImplementedError
        
        response = self._completed_to_bool(response)

        if response["completed"]:
            self.completed = True

        return response
        
    def _check_code_complete(self, code: str, output: str):
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
    
    def _check_question_complete(self, chat: Chat):
        """
        Checks if the question is correct.
        Returns the Completed or not (bool) and the reason (str).
        """

        if len(chat.messages) == 0:
            return {
                "completed": False,
                "reason": "No messages in the chat."
            }

        vars = self.to_dict()
        vars["last_chat_response"] = chat.messages[-1].message

        assert chat.messages[-1].isHuman, "Last message should be from the user."

        response = self.llm.get_response_prompt_file(
            "interview_master/prompts/question_task_complete.md",
            vars,
        )

        return response # Dict{"completed": bool, "reason": str}
    
    def _completed_to_bool(self, response: dict):
        """
        Converts the completed field in the response to a boolean.
        """

         # Convert completed to a boolean
        response["completed"] = str_to_bool(response["completed"])

        return response


    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "success_description": self.success_description,
            "completed": str(self.completed),
        }
    
    def __str__(self):
        return str(self.to_dict())
    

if __name__ == "__main__":
    # Test of the system
    from llm.clients.gemini import Gemini
    llm = Gemini("llm/clients/google.key")

    # task = Task(
    #     llm,
    #     TaskType.CODE,
    #     "Sum of two numbers",
    #     "Write a function that returns the sum of two numbers.",
    #     "There is a function defined that returns the sum of two numbers.",
    # )

    # code = """
    # def sum(a, b):
    #     return a + b

    # print(sum(1, 2))
    # """

    # output = "3"

    # print(task.check_code_complete(code, output))

    # task = Task(
    #     llm,
    #     TaskType.CODE,
    #     "Difference of two numbers",
    #     "Write a function that returns the difference of two numbers.",
    #     "There is a function defined that returns the difference of two numbers. With proof that it works properly.",
    # )

    # print(task.check_code_complete(code, output))


    task = Task(
        llm,
        TaskType.QUESTION,
        "Function Question",
        "Why do we use functions in programming?",
        "They gave a thoughtful answer to the question that is correct.",
    )

    chat = Chat()
    chat.messages.append(Message(True, "Functions are used to encapsulate code and reuse it."))
    
    print(task.check_complete("", "", chat))


