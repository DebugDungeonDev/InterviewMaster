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