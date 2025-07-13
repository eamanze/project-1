# text_processor.py
import os
import time
import fitz

class TextProcessor:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    @staticmethod
    def _get_file_size(pdf_path: str) -> str:
        """Get human-readable file size"""
        size = os.path.getsize(pdf_path)
        return f"{size} bytes" if size < 1024 else f"{size/1024:.2f}KB"

    def extract_text(self, pdf_path: str) -> str:
        """Extract and time text from PDF"""
        print(f"\n📄 Extracting {self._get_file_size(pdf_path)}")
        start = time.time()
        
        with fitz.open(pdf_path) as doc:
            text = " ".join(page.get_text() for page in doc)
        
        print(f"⏱️ Extraction: {time.time()-start:.2f}s")
        return text

    def chunk_text(self, text: str, max_tokens: int = 512) -> list[str]:
        """Token-aware text chunking"""
        print("✂️ Token-aware chunking...")
        start = time.time()
        
        inputs = self.tokenizer(
            text,
            return_overflowing_tokens=True,
            stride=50,
            max_length=max_tokens,
            truncation=False
        )
        
        chunks = [
            self.tokenizer.decode(chunk, skip_special_tokens=True).strip()
            for chunk in inputs["input_ids"]
        ]
        
        print(f"⏱️ Chunked {len(chunks)} parts in {(time.time()-start)*1000:.2f}ms")
        return chunks