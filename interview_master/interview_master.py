
from llm.chat import Chat, Message
from interview_master.task.task import Task
from interview_master.task_manager import TaskManager

from frontend.frontend_update import FrontendUpdate

class InterviewMaster:
    def __init__(self):
        self.task_manager: TaskManager = TaskManager()

    def handle_chat_message(self, update: FrontendUpdate):
        """
        Update the interview master when a new message is sent.
        """
        raise NotImplementedError
    
    def handle_code_submission(self, update: FrontendUpdate):
        """
        Update the interview master when code is submitted.
        """
        raise NotImplementedError
        
        