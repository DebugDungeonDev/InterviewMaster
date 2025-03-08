"""
Manages keeping track of the current tasks, the end tasks, the previous tasks, etc...
"""

from frontend.frontend_update import FrontendUpdate
from interview_master.task import Task, TaskType
from llm.llm import LLM
from llm.utils import str_to_bool

from typing import List

class TaskManager:
    def __init__(self):
        self.current_task: Task = None

        # The final task, kept a secret from the candidate. This is the end goal, 
        # but we'll let the candidate go off course but guide them back eventually.
        self.final_task: Task = None  
        self.previous_tasks: List[Task] = []  # The tasks that have been shown to the candidate (not all completed necessarily)

    def update(self, update: FrontendUpdate):  
        response = self.current_task.check_complete(chat=update.chat, code=update.code, output=update.code_output)
        self._update_task(update.llm, response)

    
    def _update_task(self, llm: LLM, check_response: dict):
        vars = {
            "end_name": self.final_task.name,
            "end_description": self.final_task.description,
            "end_success_description": self.final_task.success_description,
            "current_code": self.current_task.code,
            "current_output": self.current_task.code_output,
            "name": self.current_task.name,
            "description": self.current_task.description,
            "success_description": self.current_task.success_description,
            "completed": check_response['completed'],
            "reason": check_response['reason'],
        }
        response = llm.get_response_prompt_file("interview_master/prompts/update_task.md",
                                                vars)
        
        response['final_complete'] = str_to_bool(response['final_complete'])
        if response['final_complete']:
            # End the interview
            self.final_task.completed = True
            return
        
        response['stay'] = str_to_bool(response['stay'])
        if response['stay']:
            if self.current_task.completed:
                print("TASK COMPLETED BUT STAYING, VERY SUSPICIOUS (╯°□°）╯︵ ┻━┻ ")
            return  # Keep the current task
        
        # Move to the next task
        self.previous_tasks.append(self.current_task.copy())

        # Update current task using output from the LLM
        new_task_type = TaskType.Code if response['new_task_type'].lower() == "code" else TaskType.Question
        self.current_task = Task(
            llm=llm,
            task_type=new_task_type,
            name=response['new_task_name'],
            description=response['new_task_description'],
            success_description=response['new_task_success_criteria'],
        )

