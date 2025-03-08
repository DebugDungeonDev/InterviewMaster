import yaml
from llm.llm import LLM
from interview_master.task import Task, TaskType

class Scenario:
    def __init__(self, llm: LLM, scenario_file: str):
        self.llm = llm
        self.scenario_file = scenario_file
        self.build_scenario()
    
    def build_scenario(self):
        """
        Loads the YAML and generates a first task and a final task as well as starting code
        """

        with open(self.scenario_file, 'r') as stream:
            try:
                scenario = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)
        
        vars = {
            "scenario_name": scenario['name'],
            "scenario_description": scenario['description'],
            "num_tasks": str(scenario["max_tasks"]),
            "language": scenario["language"],
        }

        response = self.llm.get_response_prompt_file("interview_master/prompts/gen_init_tasks.md",
                                                vars)
        
        # Create the first task
        task_type = TaskType.CODE if response['first_task_type'].lower() == "code" else TaskType.QUESTION
        first_task = Task(
            llm=self.llm,
            task_type=task_type,
            name=response['first_task_name'],
            description=response['first_task_description'],
            success_description=response['first_task_success_criteria'],
        )

        # Create the final task
        final_task = Task(
            llm=self.llm,
            task_type=TaskType.QUESTION,
            name="Final Task",
            description=scenario['description'],
            success_description=response["final_task_success_criteria"],
        )

        self.first_task = first_task
        self.final_task = final_task
        self.starting_code = response['starting_code']

        # Remove the ``` from the starting code

        self.starting_code = self.starting_code.replace("```python", "")
        self.starting_code = self.starting_code.replace("```", "")
        self.starting_code = self.starting_code.strip()


if __name__ == "__main__":
    from llm.clients.gemini import Gemini
    from llm.chat import Chat 

    llm = Gemini("llm/clients/google.key")

    scenario = Scenario(llm, "scenarios/calcapp.yaml")
    print("First task:", scenario.first_task.to_dict())
    print("Final task:", scenario.final_task.to_dict())
    print("Starting code:", scenario.starting_code)