"""
Manages keeping track of the current tasks, the end tasks, the previous tasks, etc...
"""

from frontend.frontend_update import FrontendUpdate
from interview_master.task import Task, TaskType
from llm.llm import LLM
from llm.chat import Message
from llm.utils import str_to_bool

from typing import List
import copy

class TaskManager:
    def __init__(self, start_task: Task, final_task: Task):
        self.current_task: Task = start_task

        # The final task, kept a secret from the candidate. This is the end goal, 
        # but we'll let the candidate go off course but guide them back eventually.
        self.final_task: Task = final_task

    
        self.previous_tasks: List[Task] = []  # The tasks that have been shown to the candidate (not all completed necessarily)

    def update(self, llm: LLM, fru: FrontendUpdate) -> FrontendUpdate:  
        """
        Updates the current task and returns a message to the candidate explaining the change and why.
        """
        response = self.current_task.check_complete(chat=fru.chat, code=fru.code, output=fru.code_output)

        if self.current_task.completed:
            # Check if the final task is complete
            final_response = self.check_final_task_complete(llm, fru)
            if self.final_task.completed:
                return

        self._update_task(llm, fru, response)
        
        fru.chat.messages.append(Message(
            False,
            response['reason']
        ))
        
        return fru

    
    def _update_task(self, llm: LLM, fru: FrontendUpdate, check_response: dict):

        last_3_chat_messages = fru.chat.get_last_n_messages_str(3)

        vars = {
            "tasks_completed": str(len(self.previous_tasks)),
            "end_name": self.final_task.name,
            "end_description": self.final_task.description,
            "end_success_description": self.final_task.success_description,
            "code": fru.code,
            "output": fru.code_output,
            "chat_messages": last_3_chat_messages,
            "name": self.current_task.name,
            "description": self.current_task.description,
            "success_description": self.current_task.success_description,
            "completed": str(check_response['completed']),
            "reason": check_response['reason'],
        }
        response = llm.get_response_prompt_file("interview_master/prompts/update_task.md",
                                                vars)
        
        # response['final_complete'] = str_to_bool(response['final_complete'])
        # if response['final_complete']:
        #     # End the interview
        #     self.final_task.completed = True
        #     return
        
        response['stay'] = str_to_bool(response['stay'])
        if response['stay']:
            if self.current_task.completed:
                print("TASK COMPLETED BUT STAYING, VERY SUSPICIOUS (╯°□°）╯︵ ┻━┻ ")
            return  # Keep the current task
        
        # Move to the next task
        self.previous_tasks.append(copy.deepcopy(self.current_task))

        # Update current task using output from the LLM
        new_task_type = TaskType.CODE if response['new_task_type'].lower() == "code" else TaskType.Question
        self.current_task = Task(
            llm=llm,
            task_type=new_task_type,
            name=response['new_task_name'],
            description=response['new_task_description'],
            success_description=response['new_task_success_criteria'],
        )

    def check_final_task_complete(self, llm: LLM, fru: FrontendUpdate):
        """
        By looking at a summary of the tasks completed, the code, the output, and the chat messages,
        the LLM will decide if the final task is complete and the interview should end.
        """
        completed_tasks = [task for task in self.previous_tasks if task.completed]
        tasks_completed_descriptions = [task.name + ": " + task.success_description for task in completed_tasks]
        tasks_completed_str = "\n".join(tasks_completed_descriptions)
        
        vars = {
            "tasks_completed_descriptions": tasks_completed_str,
            "end_name": self.final_task.name,
            "end_description": self.final_task.description,
            "end_success_description": self.final_task.success_description,
            "code": fru.code,
            "output": fru.code_output,
            "chat_messages": fru.chat.get_last_n_messages_str(3),
        }

        response = llm.get_response_prompt_file("interview_master/prompts/final_task_complete.md",
                                                vars)

        response['end_interview'] = str_to_bool(response['end_interview'])
        if response['end_interview']:
            self.final_task.completed = True
        
        return response
        


if __name__ == "__main__":

    from llm.clients.gemini import Gemini
    from llm.chat import Chat 

    llm = Gemini("llm/clients/google.key")

    t1 = Task(llm, TaskType.CODE, "Task 1",
                "Write a function that takes two numbers and returns the sum",
                "The code has a function that returns the sum of two numbers.")
    
    final_task = Task(llm, TaskType.CODE, "Final Task",
                "Write a calculator script that has add, subtract, multiply, and divide functions",
                "The code meets the functions required and runs well with proof as shown by the candidate's print statements, and the candidate has demonstrated a good understanding of why we use fuunctions via questions and answers.")
    
    # Test the TaskManager
    tm = TaskManager(t1, final_task)
    
    code = """
    def sum(a, b):
        return a + b

    print(sum(1, 2))
    """

    code_output = "3"

    fru = FrontendUpdate(Chat(), code, code_output, t1)

    tm.update(llm, fru)

    print(tm.current_task.to_dict())