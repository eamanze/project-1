from ai_agents import GenerativeAI

class ResponseService:
    def __init__(self):
        self.generator = GenerativeAI()
    
    def generate_answer(self, file_id, text):
        question = "What is the main topic of this document?"
        return self.generator.generate_response(file_id, question, text[:2000])
    
    def generate_answer_from_context(self, query: str, context: str, file_id: str = "search"):
        return self.generator.generate_response(file_id, query, context)
