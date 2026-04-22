import math
import re
import json

class BM25Engine:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0
        self.doc_lengths = []
        self.doc_freqs = {}
        self.inverted_index = {}
        self.documents = []  # Stores doc metadata

    def tokenize(self, text):
        if not text:
            return []
        # Support CJK by splitting characters if needed, but here we use a simple regex
        # This regex treats sequences of alphanumeric as a word, and single CJK chars as tokens
        tokens = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        results = []
        for token in tokens:
            # If CJK, split into characters for better matching
            if any('\u4e00' <= c <= '\u9fff' for c in token):
                results.extend(list(token))
            else:
                results.append(token)
        return results

    def add_documents(self, docs_with_text):
        """
        docs_with_text: List of dicts with {'id': ..., 'text': ...}
        """
        self.documents = docs_with_text
        self.corpus_size = len(docs_with_text)
        total_len = 0
        
        for i, doc in enumerate(docs_with_text):
            tokens = self.tokenize(doc.get('text', ''))
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len
            
            # Count word frequencies in doc
            word_counts = {}
            for token in tokens:
                word_counts[token] = word_counts.get(token, 0) + 1
            
            # Update inverted index and global doc frequencies
            for token, count in word_counts.items():
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append((i, count))
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                
        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size > 0 else 0

    def get_scores(self, query):
        query_tokens = self.tokenize(query)
        scores = [0.0] * self.corpus_size
        
        for token in query_tokens:
            if token not in self.inverted_index:
                continue
            
            # Precompute IDF
            df = self.doc_freqs[token]
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)
            
            for doc_idx, freq in self.inverted_index[token]:
                doc_len = self.doc_lengths[doc_idx]
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                scores[doc_idx] += idf * (numerator / denominator)
                
        return scores

    def search(self, query, top_n=5):
        if not self.documents:
            return []
        scores = self.get_scores(query)
        indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in indices[:top_n]:
            if scores[i] <= 0:
                continue
            res = self.documents[i].copy()
            res['score'] = round(scores[i], 4)
            results.append(res)
        return results

    def to_json(self):
        return {
            "k1": self.k1,
            "b": self.b,
            "corpus_size": self.corpus_size,
            "avg_doc_len": self.avg_doc_len,
            "doc_lengths": self.doc_lengths,
            "doc_freqs": self.doc_freqs,
            "inverted_index": self.inverted_index,
            "documents": self.documents
        }

    @classmethod
    def from_json(cls, data):
        obj = cls(k1=data["k1"], b=data["b"])
        obj.corpus_size = data["corpus_size"]
        obj.avg_doc_len = data["avg_doc_len"]
        obj.doc_lengths = data["doc_lengths"]
        obj.doc_freqs = data["doc_freqs"]
        obj.inverted_index = data["inverted_index"]
        obj.documents = data["documents"]
        return obj
