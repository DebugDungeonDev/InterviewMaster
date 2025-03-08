
from llm.chat import Chat, Message
from interview_master.task.task import Task, TaskType
from interview_master.task_manager import TaskManager

from frontend.frontend_update import FrontendUpdate
from scenario import Scenario
from llm.llm import LLM

class InterviewMaster:
    def __init__(self, scenario: Scenario):
        self.scenario: Scenario = scenario
        self.task_manager: TaskManager = TaskManager(self.scenario.first_task, self.scenario.final_task)

    def handle_start(self, llm: LLM) -> FrontendUpdate:
        """
        Handle the start of the interview.
        """
        
        # Get the first task
        fru = FrontendUpdate(
            Chat(),
            self.scenario.starting_code,
            "",
            self.scenario.first_task
        )

        return fru

    def handle_chat_message(self, llm: LLM, fru: FrontendUpdate) -> FrontendUpdate:
        """
        Update the interview master when a new message is sent.
        """
        
        # If current on a question task, check if the question is complete
        if self.task_manager.current_task.task_type == TaskType.QUESTION:
            fru = self.task_manager.update(llm, fru)

        # Give a response to the candidate
        fru.chat.messages.append(Message(
            False,
            llm.get_multiturn_response(fru.chat, 5, self.task_manager.current_task)
        ))

        return fru
    
    def handle_code_submission(self, llm: LLM, fru: FrontendUpdate) -> FrontendUpdate:
        """
        Update the interview master when code is submitted.
        """
        
        # Check if they completed the code task
        fru = self.task_manager.update(llm, fru)

        return fru
        
        