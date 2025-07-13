from base_agent import BaseAgent
from file_processor_agent import FileProcessorAgent

class TextProcessorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="TextProcessorAgent")
        self.file_processor = FileProcessorAgent()

    def run(self):
        print(f"[{self.name}] Starting file processing...")
        self.file_processor.run(file_type="pdf", file_data=None)