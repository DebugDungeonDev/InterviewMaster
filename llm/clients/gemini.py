# import google.generativeai as genai
from google import genai
import time 
from google.genai import types
from llm.llm import LLM

class Gemini(LLM):
    def __init__(self, keys_file):
        super().__init__()
        self.keys = [key.strip() for key in open(keys_file, "r").readlines()]
        self.current_key_index = 0


    def _get_max_rpm(self):
        return len(self.keys) * 14
    
    def get_basic_response(self, prompt):
        # genai.configure(api_key=self.keys[self.current_key_index])

        # self.model = genai.GenerativeModel("gemini-2.0-flash")
        done = False 
        while not done: 
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            client = genai.Client(api_key=self.keys[self.current_key_index])

            try:
       
                response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt
                    )
                                                        
                done = True
            except ValueError as e:  # TODO: Replace with a better exception
                print("API Exception: ", e)
                print("Sleeping, and switching to next key")
                time.sleep(10)
            except Exception as e:
                print("Exception: ", e)
                print("Sleeping, and switching to next key")
                time.sleep(10)
        return response.text