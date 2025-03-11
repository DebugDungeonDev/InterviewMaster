
from llm.chat import Chat, Message
from interview_master.task import Task, TaskType
from interview_master.task_manager import TaskManager

from frontend.frontend_update import FrontendUpdate
from interview_master.scenario import Scenario
from llm.llm import LLM
import logging

class InterviewMaster:
    def __init__(self, scenario: Scenario, logger: logging.Logger = None):
        self.scenario: Scenario = scenario
        self.task_manager: TaskManager = TaskManager(self.scenario.first_task, self.scenario.final_task)
        self.logger = logger

        if self.logger is None:
            self.logger = logging.getLogger("InterviewMaster")
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())

    def handle_start(self) -> FrontendUpdate:
        """
        Handle the start of the interview.
        """

        self.logger.info("Starting the interview.")
        
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
        # if self.task_manager.current_task.task_type == TaskType.QUESTION:
        fru = self.task_manager.update(llm, fru)

        vars = {
            "name": fru.current_task.name,
            "description": fru.current_task.description,
            "success_description": fru.current_task.success_description,
            "last_chat_messages": fru.chat.get_last_n_messages_str(5),
            "code": fru.code,
            "output": fru.code_output,
        }
        response = llm.get_response_prompt_file(
            "interview_master/prompts/general_chatting.md",
            vars
        )

        # Give a response to the candidate
        fru.chat.messages.append(Message(
            False,
            response['response']
        ))

        return fru
    
    def handle_code_submission(self, llm: LLM, fru: FrontendUpdate) -> FrontendUpdate:
        """
        Update the interview master when code is submitted.
        """

        fru.chat.messages.append(Message(True, "Code submitted."))

        if self.task_manager.current_task.task_type == TaskType.CODE:
            fru = self.task_manager.update(llm, fru)

        return fru
        

if __name__ == "__main__":
    from llm.clients.gemini import Gemini
    from llm.chat import Chat 
    llm = Gemini("llm/clients/google.key")
    scenario = Scenario(llm, "scenarios/medianstocks.yaml")
    im = InterviewMaster(scenario)
    fru = im.handle_start()
    print(fru)
    fru.chat.messages.append(Message(True, "Hello, I need help getting started."))
    fru = im.handle_chat_message(llm, fru)
    print(fru)

    fru.code = "def add(a, b):\n    return a + b"
    fru = im.handle_code_submission(llm, fru)
    print(fru)