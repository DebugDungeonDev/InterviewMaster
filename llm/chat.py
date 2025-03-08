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
        Get the last n messages as a string, ordered from oldest to newest.
        """
        
        # Slice the last n messages in the correct order
        last_messages = self.messages[-n:]  # This preserves order (oldest to newest)
        
        out = ""
        for msg in last_messages:
            out += "Candidate: " if msg.isHuman else "Interviewer: "
            out += msg.message + "\n"
    
        return out

    
    def to_history(self):
        history = []
        for msg in self.messages:
            role = "user" if msg.isHuman else "assistant"
            content = msg.message
            history.append({"role": role, "content": content})
        return history
    
    def __str__(self):
        return self.get_last_n_messages_str(len(self.messages))
