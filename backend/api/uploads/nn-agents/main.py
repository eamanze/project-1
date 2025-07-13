import time
from text_processor_agent import TextProcessorAgent
from query_responder_agent import QueryResponderAgent

if __name__ == "__main__":
    start = time.perf_counter()

    processor = TextProcessorAgent()
    processor.run()

    responder = QueryResponderAgent()

    while True:
        query = input("\nAsk a question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        context = responder.retrieve_context(query)
        if not context:
            print("No relevant context found.")
            continue

        answer = responder.generate_answer(context, query)
        print("\nAI Answer:\n", answer)

    end = time.perf_counter()
    print(f"\nCompleted in {end - start:.2f} seconds.")