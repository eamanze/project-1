from celery import shared_task
import file_processor_agent as fp
import embedder_agent as ea
import time

@shared_task
def process_text(file_hash, s3_uri):
    start_time = time.time()

    #file_processor = fp.FileProcessorAgent(file_hash, s3_uri)
    #file_processor.run()

    end_time = time.time()
    elapsed_time = end_time - start_time
    return f"Text for {file_hash} processed successfully in {elapsed_time:.2f} seconds."

@shared_task
def generate_embeddings(file_hash):
    start_time = time.time()

    #embedder = ea.EmbedderAgent()
    #embedder.run(file_hash)  

    end_time = time.time()
    elapsed_time = end_time - start_time
    return f"Embeddings for {file_hash} generated and saved successfully in {elapsed_time:.2f} seconds."
