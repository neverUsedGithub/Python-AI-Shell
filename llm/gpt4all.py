from gpt4all import GPT4All # type: ignore

class Model:
    def __init__(self) -> None:
        self.system_prompt = ""
        self.model = GPT4All(
            "mistral-7b-instruct-v0.1.Q4_0.gguf",
            model_path="./models/",
            device="gpu",
            verbose=False
        )
        self.messages = []
        self._chat_session = None
    
    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt

    def chat_start(self):
        self.messages = [
            { "role": "system", "content": self.system_prompt }
        ]
        self._chat_session = self.model.chat_session(system_prompt=self.system_prompt)
        self._chat_session.__enter__()
    
    def chat_add_message(self, role: str, content: str):
        if not self._chat_session:
            raise Exception("Chat has not been started yet.")

        self.messages.append({ "role": role, "content": content })
        self.model.current_chat_session.append({ "role": role, "content": content })

    def chat_generate(self, prompt: str, temp: int = 0, max_tokens: int = 100):
        if not self._chat_session:
            raise Exception("Chat has not been started yet.")

        for token in self.model.generate(prompt, temp=temp, max_tokens=max_tokens, streaming=True):
            yield token

    def chat_close(self):
        if not self._chat_session:
            raise Exception("Chat has not been started yet.")
        
        self._chat_session.__exit__(None, None, None)
        self._chat_session = None
