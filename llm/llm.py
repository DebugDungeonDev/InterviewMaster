"""
Abstract llm class that can handle prompts and return a response to the user.
"""

class LLM:
    def __init__(self):
        pass

    def get_response(self, prompt):
        """
        Returns a response to the prompt.
        """
        raise NotImplementedError

    def get_name(self):
        """
        Returns the name of the LLM.
        """
        raise NotImplementedError

    def get_description(self):
        """
        Returns the description of the LLM.
        """
        raise NotImplementedError