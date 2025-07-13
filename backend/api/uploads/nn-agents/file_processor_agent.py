
from base_agent import BaseAgent
import boto3
import pdfplumber
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import *
from agents.db_utils import save_chunk_to_db

s3_client = boto3.client('s3')

class FileProcessorAgent(BaseAgent):
    def __init__(self, file_hash: str, s3_uri: str):
        super().__init__(name="FileProcessorAgent")
        self.file_hash = file_hash
        self.s3_uri = s3_uri

    def run(self):
        print(f"[{self.name}] Processing file {self.file_hash} from {self.s3_uri}...")
        
        file_type = self.detect_file_type(self.s3_uri)

        if file_type == "pdf":
            self.process_pdf()
        else:
            raise ValueError(f"[{self.name}] Unsupported file type detected for {self.file_hash}")

    def detect_file_type(self, s3_uri):
        if s3_uri.lower().endswith(".pdf"):
            return "pdf"
        else:
            return None

    def process_pdf(self):
        texts = self.extract_texts_from_s3(single_s3_uri=self.s3_uri)
        if texts:
            self.save_text_chunks(texts, file_hash=self.file_hash)
            print(f"[{self.name}] Text extracted and chunks saved for PDF {self.file_hash}")
        else:
            print(f"[{self.name}] No text extracted from PDF {self.file_hash}")

    def extract_texts_from_s3(self, bucket_name=None, prefix=None, single_s3_uri=None):
        if single_s3_uri:
            bucket_name, key = self.parse_s3_uri(single_s3_uri)
            pdf_keys = [key]
        else:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' not in response:
                print("No PDF files found.")
                return []
            pdf_keys = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]

        texts = []

        def download_and_extract(key):
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
            file_stream = BytesIO(s3_object['Body'].read())
            with pdfplumber.open(file_stream) as pdf:
                return "\n".join(filter(None, [page.extract_text() for page in pdf.pages if page.extract_text()]))

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(download_and_extract, pdf_keys))

        return [text for text in results if text]

    def save_text_chunks(self, texts, file_hash):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = text_splitter.create_documents(texts)

        for i, chunk in enumerate(chunks):
            save_chunk_to_db(
                file_hash=file_hash,
                chunk_text=chunk.page_content,
                chunk_number=i,
                vector_id=None,
                model_used="textembedding-gecko@latest"
            )
        print(f"Saved {len(chunks)} chunks to DB for file {file_hash}.")

    def parse_s3_uri(self, s3_uri):
        assert s3_uri.startswith("s3://"), "Invalid S3 URI"
        parts = s3_uri[5:].split("/", 1)
        return parts[0], parts[1]
    