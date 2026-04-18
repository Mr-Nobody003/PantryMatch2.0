import math
import re
from collections import defaultdict
import numpy as np

ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against", "all",
    "almost", "alone", "along", "already", "also", "although", "always", "am", "among",
    "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone",
    "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be",
    "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand",
    "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could",
    "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during",
    "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough",
    "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except",
    "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former",
    "formerly", "forty", "found", "four", "from", "front", "full", "further", "get",
    "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here",
    "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself",
    "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly",
    "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill",
    "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my",
    "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine",
    "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere",
    "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other",
    "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part",
    "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem",
    "seemed", "seeming", "seems", "serious", "several", "she", "should", "show",
    "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such", "system",
    "take", "ten", "than", "that", "the", "their", "them", "themselves", "then",
    "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon",
    "these", "they", "thick", "thin", "third", "this", "those", "though", "three",
    "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward",
    "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon",
    "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein",
    "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever",
    "whole", "whom", "whose", "why", "will", "with", "within", "without", "would",
    "yet", "you", "your", "yours", "yourself", "yourselves"
])

class SimpleTfidfVectorizer:
    def __init__(self, stop_words="english"):
        self.stop_words = ENGLISH_STOP_WORDS if stop_words == "english" else set()
        self.vocab = {}
        self.idf = []
    
    def _tokenize(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stop_words and not w.isdigit()]
        
    def fit_transform(self, raw_documents):
        doc_tfs = []
        df = defaultdict(int)
        
        for doc in raw_documents:
            words = self._tokenize(doc)
            tf = defaultdict(int)
            for w in words:
                tf[w] += 1
            doc_tfs.append(tf)
            for w in set(words):
                df[w] += 1
                
        num_docs = len(raw_documents)
        vocab_list = sorted(list(df.keys()))
        self.vocab = {w: i for i, w in enumerate(vocab_list)}
        self.idf = np.zeros(len(self.vocab), dtype=np.float32)
        
        for w, idx in self.vocab.items():
            self.idf[idx] = math.log((num_docs + 1) / (df[w] + 1)) + 1.0
            
        matrix = np.zeros((num_docs, len(self.vocab)), dtype=np.float32)
        for i, tf in enumerate(doc_tfs):
            for w, count in tf.items():
                if w in self.vocab:
                    idx = self.vocab[w]
                    matrix[i, idx] = count * self.idf[idx]
                    
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return matrix / norms
        
    def transform(self, raw_documents):
        num_docs = len(raw_documents)
        matrix = np.zeros((num_docs, len(self.vocab)), dtype=np.float32)
        for i, doc in enumerate(raw_documents):
            words = self._tokenize(doc)
            tf = defaultdict(int)
            for w in words:
                tf[w] += 1
            for w, count in tf.items():
                if w in self.vocab:
                    idx = self.vocab[w]
                    matrix[i, idx] = count * self.idf[idx]
                    
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return matrix / norms

def simple_cosine_similarity(vec, matrix):
    return np.dot(vec, matrix.T)
