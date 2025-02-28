from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv(override=True)

class CodeGen():
    def __init__(self, system, model_name='gpt-4o', temperature=0.5):
    
        self.model = OpenAI()
        self.model_name = model_name
        self.temperature = temperature

        self.messages = []
        self.messages = [{'role': 'system', 'content': system}]

        tools_path = os.path.join(os.path.dirname(__file__), 'tools.json')
        
        with open(tools_path, 'r') as f:
            self.tools = json.load(f)

    def __call__(self, prompt=None, tool_choice='auto'):
    
        if prompt:  
            tool_choice = 'required'
            self.messages.append({'role': 'user', 'content': prompt})

        completion = self.model.chat.completions.create(
                        model=self.model_name,
                        messages=self.messages,
                        tools = self.tools,
                        tool_choice=tool_choice,
                        temperature=self.temperature
                    )
        
        response = completion.choices[0].message.content

        self.messages.append({'role': 'assistant', 'content': str(response)})

        tool_calls = completion.choices[0].message.tool_calls
        
        if tool_calls:
            self.messages.append(completion.choices[0].message)
            return self.retrieve(tool_calls)
        else:
            return response
    

    def retrieve(self, tool_calls):
        try:
            return json.loads(tool_calls[0].function.arguments).get("content")
        except Exception as e:
            raise Exception(f"Error: {e}")

    