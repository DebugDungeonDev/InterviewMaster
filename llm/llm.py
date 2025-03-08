"""
Abstract llm class that can handle prompts and return a response to the user.
"""

from typing import Dict
from llm.chat import Chat, Message


class LLM:
    def __init__(self):
        pass

    def get_basic_response(self, prompt: str):
        """
        Returns a basic response to the prompt.
        """
        raise NotImplementedError
    
    def get_multiturn_response(self, chat: Chat, n: int, current_task):
        """
        Takes the n last messages from the chat and returns a response.
        """
        messages = chat.get_last_n_messages_str(n)
        prompt = "Current task for the candidate:\n"
        prompt += str(current_task.to_dict()) + "\n"
        prompt += "Chat between an technical interviewer and a candidate:\n"
        prompt += messages
        
        return self.get_basic_response(prompt)

    
    def get_response_prompt_file(self, prompt_file: str, vars: Dict = {}) -> Dict:
        """
        Loads the prompt file, replaces the variables with the values in the vars dictionary,
        and returns the response from the LLM. The response is parsed for any tags and their values
        and returned in a dictionary.
        """
        with open(prompt_file, 'r') as f:
            prompt = f.read()

        for key, value in vars.items():
            # Raise error if nothing to replace
            if key not in prompt:
                raise ValueError(f"Key {key} not found in prompt file {prompt_file}")
            
            key_aug = "{{" + key + "}}"
            prompt = prompt.replace(key_aug, value)

        # Raise error if any keys are left
        if "{{" in prompt or "}}" in prompt:
            raise ValueError(f"Keys left in prompt file {prompt_file} {prompt}")

        response = self.get_basic_response(prompt)

        tags = self._get_tags(response)

        return tags
    

    def _get_tags(self, response: str) -> Dict:
        """
        Parses the response for any tags and their values and returns them in a dictionary.
        """
        tags = {}
        while True:
            start = response.find("<")
            if start == -1:
                break
            
            # Continue till the > is found to get the tag name
            end = response.find(">", start)
            if end == -1:
                break

            tag_name = response[start+1:end]
            tag_value = response[end+1:response.find(f"</{tag_name}>")]

            tags[tag_name] = tag_value

            true_end = response.find(f"</{tag_name}>")
            true_end += len(f"</{tag_name}>")

            # Trim the response
            response = response[0:start] + response[true_end:]
        
        return tags

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