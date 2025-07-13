from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM
import torch
import numpy as np
import time
import os

class EmbeddingGenerator:
    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "intfloat/e5-base-v2")
        self.tokenizer = None
        self.model = None
        self._loaded = False

    def _load_model(self):
        if self._loaded: return
        
        try:
            start = time.time()
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            tokenizer_time = (time.time() - start) * 1000
            
            start = time.time()
            self.model = AutoModel.from_pretrained(self.model_name)
            model_time = (time.time() - start) * 1000
            
            print(f"⏱️ Model loading times ({self.model_name}):")
            print(f"- Tokenizer: {tokenizer_time:.2f}ms")
            print(f"- Model: {model_time:.2f}ms")
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")

    def generate_embeddings(self, texts: list[str], file_id: str) -> list[list[float]]:
        if not self._loaded:
            self._load_model()
        start_time = time.time()
        batch = ["passage: " + text for text in texts]
        
        encode_start = time.time()
        encoded_input = self.tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        )
        encode_time = (time.time() - encode_start) * 1000
        
        infer_start = time.time()
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        infer_time = (time.time() - infer_start) * 1000
        
        pool_start = time.time()
        token_embeddings = model_output.last_hidden_state
        attention_mask = encoded_input["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        pool_time = (time.time() - pool_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
        text_preprocessing_time = total_time - (encode_time + infer_time + pool_time)
        
        print(f"\n⏱️ Embedding generation metrics for file:", file_id)
        print(f"- Text preprocessing: {text_preprocessing_time:.2f}ms")
        print(f"- Tokenization: {encode_time:.2f}ms")
        print(f"- Model inference: {infer_time:.2f}ms")
        print(f"- Pooling: {pool_time:.2f}ms")
        
        return embeddings.numpy().tolist()

class GenerativeAI:
    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv("GENERATIVE_MODEL", "google/flan-t5-base")
        self.tokenizer = None
        self.model = None
        self._loaded = False

    def _load_model(self):
        if self._loaded: return
        
        try:
            start = time.time()
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            tokenizer_time = (time.time() - start) * 1000
            
            start = time.time()
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            model_time = (time.time() - start) * 1000
            
            print(f"\n⏱️ Generative model loading times ({self.model_name}):")
            print(f"- Tokenizer: {tokenizer_time:.2f}ms")
            print(f"- Model: {model_time:.2f}ms")
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load generative model: {str(e)}")

    def generate_response(self, file_id: str, prompt: str, context: str = "") -> str:
        if not self._loaded:
            self._load_model()
        start_time = time.time()
        input_text = f"Question: {prompt}\nContext: {context}\nAnswer:" if context else f"Question: {prompt}\nAnswer:"
        
        token_start = time.time()
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        token_time = (time.time() - token_start) * 1000
        
        gen_start = time.time()
        outputs = self.model.generate(
            inputs.input_ids,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
        )
        gen_time = (time.time() - gen_start) * 1000
        
        decode_start = time.time()
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        decode_time = (time.time() - decode_start) * 1000
        
        total_time = (time.time() - start_time) * 1000
        
        print(f"\n⏱️ GenAI Response generation metrics for the doc:", file_id)
        print(f"- Total time: {total_time:.2f}ms")
        print(f"- Tokenization: {token_time:.2f}ms")
        print(f"- Generation: {gen_time:.2f}ms")
        print(f"- Decoding: {decode_time:.2f}ms")
        
        return response