"""
Manages the chat between the user and the bot.
Keeps track of the entire conversation.
"""

from typing import List 

class Message:
    def __init__(self, isHuman: bool, message: str):
        self.isHuman = isHuman
        self.message = message

class Chat:
    def __init__(self):
        self.messages: List[Message] = []

    def get_last_n_messages_str(self, n: int):
        """
        Get the last n messages as a string.
        """
        
        # Utilize the isHuman flag to mark in the string
        out = ""
        capped_n = min(n, len(self.messages))
        for i in range(1, capped_n + 1):
            out += "Candidate: " if self.messages[-i].isHuman else "Interviewer: "
            out += self.messages[-i].message + "\n"
        return out