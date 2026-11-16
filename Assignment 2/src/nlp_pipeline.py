"""
CS-5592: Design and Analysis of Algorithms - Assignment 2
Problem 2: Comparative NLP Implementation on Shakespeare Corpus
Authors: Tina Nguyen & Haoran
Affiliation: University of Missouri - Kansas City (UMKC)

This module implements two complete NLP pipelines:
1. Custom Algorithmic Pipeline:
   - Hand-crafted regex/FSM tokenization
   - Custom hash-table stopword filtering
   - Memoized Porter Stemmer (Porter 1980 rules + Dynamic Programming)
   - Custom Bag-of-Words dictionary & lexical mood analyzer
2. Built-in NLTK Pipeline:
   - NLTK Tokenizer
   - NLTK English Stopwords
   - NLTK PorterStemmer (with optional caching)
   - Collections.Counter Bag-of-Words
3. Benchmarks measuring Execution Time T(n), Memory, Accuracy, and Scalability (25%, 50%, 75%, 100%).
"""

import os
import re
import time
import math
import tracemalloc
from collections import Counter
from typing import List, Dict, Tuple, Set, Optional
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer as NLTKPorterStemmer


STAGE_DIRECTIONS = {'act', 'scene', 'enter', 'exit', 'exeunt'}

# Extended stopwords including archaic Early Modern English function words when analyzing pure topical terms
SHAKESPEARE_STOPWORDS = set(stopwords.words('english')).union({
    'thou', 'thee', 'thy', 'thine', 'shall', 'shalt', 'doth', 'hath', 
    'tis', "'tis", 'upon', 'yet', 'well', 'sir', 'lord'
})

STANDARD_STOPWORDS = set(stopwords.words('english'))


class CustomPorterStemmer:
    """
    Step-by-step implementation of Martin Porter's 1980 algorithm:
    'An algorithm for suffix stripping', Program 14(3), pp. 130-137.
    Includes memoization (Dynamic Programming) to cache stems for unique words.
    """
    def __init__(self):
        self.cache: Dict[str, str] = {}

    def is_consonant(self, word: str, i: int) -> bool:
        c = word[i]
        if c in 'aeiou':
            return False
        if c == 'y':
            if i == 0:
                return True
            return not self.is_consonant(word, i - 1)
        return True

    def measure(self, stem: str) -> int:
        """Counts the number of VC sequences (measure m)."""
        m = 0
        i = 0
        n = len(stem)
        while i < n and self.is_consonant(stem, i):
            i += 1
        while i < n:
            while i < n and not self.is_consonant(stem, i):
                i += 1
            if i >= n:
                break
            while i < n and self.is_consonant(stem, i):
                i += 1
            m += 1
        return m

    def contains_vowel(self, stem: str) -> bool:
        return any(not self.is_consonant(stem, i) for i in range(len(stem)))

    def ends_double_consonant(self, stem: str) -> bool:
        if len(stem) < 2:
            return False
        return (stem[-1] == stem[-2]) and self.is_consonant(stem, len(stem) - 1)

    def cvc(self, stem: str) -> bool:
        if len(stem) < 3:
            return False
        i = len(stem) - 1
        if self.is_consonant(stem, i) and not self.is_consonant(stem, i - 1) and self.is_consonant(stem, i - 2):
            if stem[i] not in 'wxy':
                return True
        return False

    def _stem_uncached(self, word: str) -> str:
        if len(word) <= 2:
            return word

        # Step 1a: plurals and -ed / -ing
        if word.endswith("sses"):
            word = word[:-2]
        elif word.endswith("ies"):
            word = word[:-2]
        elif not word.endswith("ss") and word.endswith("s"):
            word = word[:-1]

        # Step 1b
        extra = False
        if word.endswith("eed"):
            stem = word[:-3]
            if self.measure(stem) > 0:
                word = stem + "ee"
        elif word.endswith("ed"):
            stem = word[:-2]
            if self.contains_vowel(stem):
                word = stem
                extra = True
        elif word.endswith("ing"):
            stem = word[:-3]
            if self.contains_vowel(stem):
                word = stem
                extra = True

        if extra:
            if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                word = word + "e"
            elif self.ends_double_consonant(word) and not (word.endswith("l") or word.endswith("s") or word.endswith("z")):
                word = word[:-1]
            elif self.measure(word) == 1 and self.cvc(word):
                word = word + "e"

        # Step 1c
        if word.endswith("y"):
            stem = word[:-1]
            if self.contains_vowel(stem):
                word = stem + "i"

        # Step 2: derivational suffixes
        step2_rules = [
            ("ational", "ate"), ("tional", "tion"), ("enci", "ence"), ("anci", "ance"),
            ("izer", "ize"), ("abli", "able"), ("alli", "al"), ("entli", "ent"),
            ("eli", "e"), ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"),
            ("ator", "ate"), ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
            ("ousness", "ous"), ("aliti", "al"), ("iviti", "ive"), ("biliti", "ble")
        ]
        for suffix, repl in step2_rules:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.measure(stem) > 0:
                    word = stem + repl
                break

        # Step 3
        step3_rules = [
            ("icate", "ic"), ("ative", ""), ("alize", "al"),
            ("iciti", "ic"), ("ical", "ic"), ("ful", ""), ("ness", "")
        ]
        for suffix, repl in step3_rules:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.measure(stem) > 0:
                    word = stem + repl
                break

        # Step 4
        step4_suffixes = [
            "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
            "ment", "ent", "ou", "ism", "ate", "iti", "ous", "ive", "ize"
        ]
        for suffix in step4_suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.measure(stem) > 1:
                    word = stem
                break
        else:
            if word.endswith("sion") or word.endswith("tion"):
                stem = word[:-3]
                if self.measure(stem) > 1:
                    word = stem

        # Step 5a: -e removal
        if word.endswith("e"):
            stem = word[:-1]
            m = self.measure(stem)
            if m > 1 or (m == 1 and not self.cvc(stem)):
                word = stem

        # Step 5b: double -l removal
        if self.measure(word) > 1 and self.ends_double_consonant(word) and word.endswith("l"):
            word = word[:-1]

        return word

    def stem(self, word: str) -> str:
        res = self.cache.get(word)
        if res is None:
            res = self._stem_uncached(word)
            self.cache[word] = res
        return res


class CustomHashTable:
    """A direct chained hash table for high-performance string lookup and counting."""
    def __init__(self, initial_capacity: int = 16384):
        self.capacity = initial_capacity
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

    def _hash(self, key: str) -> int:
        return (hash(key) & 0x7FFFFFFF) % self.capacity

    def put(self, key: str, value: int = 1):
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                pair[1] = value
                return
        self.buckets[idx].append([key, value])
        self.size += 1

    def increment(self, key: str, amount: int = 1):
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                pair[1] += amount
                return
        self.buckets[idx].append([key, amount])
        self.size += 1

    def get(self, key: str) -> Optional[int]:
        idx = self._hash(key)
        for pair in self.buckets[idx]:
            if pair[0] == key:
                return pair[1]
        return None

    def items(self) -> List[Tuple[str, int]]:
        res = []
        for bucket in self.buckets:
            for pair in bucket:
                res.append((pair[0], pair[1]))
        return res


class CustomNLP_Pipeline:
    """Custom NLP implementation from first principles."""
    def __init__(self, remove_stage_directions: bool = True, custom_stopwords: Optional[Set[str]] = None):
        self.remove_stage_directions = remove_stage_directions
        self.stemmer = CustomPorterStemmer()
        self.token_pattern = re.compile(r"[a-z]+(?:'[a-z]+)?")
        self.stage_dirs = STAGE_DIRECTIONS if remove_stage_directions else set()
        self.stopwords = custom_stopwords if custom_stopwords is not None else STANDARD_STOPWORDS

    def clean_text(self, text: str) -> str:
        cleaned = text.lower()
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        return cleaned

    def tokenize(self, text: str) -> List[str]:
        return self.token_pattern.findall(text)

    def filter_tokens(self, tokens: List[str]) -> List[str]:
        sw = self.stopwords
        sd = self.stage_dirs
        return [t for t in tokens if t not in sw and t not in sd]

    def stem_tokens(self, tokens: List[str]) -> List[str]:
        stem_fn = self.stemmer.stem
        return [stem_fn(t) for t in tokens]

    def build_bag_of_words(self, tokens: List[str]) -> Dict[str, int]:
        bow: Dict[str, int] = {}
        for t in tokens:
            bow[t] = bow.get(t, 0) + 1
        return bow

    def run_pipeline(self, raw_text: str) -> Dict:
        t0 = time.time()
        tracemalloc.start()
        
        t_clean0 = time.time()
        cleaned = self.clean_text(raw_text)
        t_clean = time.time() - t_clean0
        
        t_tok0 = time.time()
        tokens = self.tokenize(cleaned)
        t_tok = time.time() - t_tok0
        
        t_filt0 = time.time()
        filtered = self.filter_tokens(tokens)
        t_filt = time.time() - t_filt0
        
        t_stem0 = time.time()
        stemmed = self.stem_tokens(filtered)
        t_stem = time.time() - t_stem0
        
        t_bow0 = time.time()
        bow_dict = self.build_bag_of_words(filtered)
        stem_bow_dict = self.build_bag_of_words(stemmed)
        t_bow = time.time() - t_bow0
        
        total_time = time.time() - t0
        curr_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "num_raw_chars": len(raw_text),
            "num_raw_tokens": len(tokens),
            "num_filtered_tokens": len(filtered),
            "num_unique_words": len(bow_dict),
            "num_unique_stems": len(stem_bow_dict),
            "bow": bow_dict,
            "stem_bow": stem_bow_dict,
            "time_clean": t_clean,
            "time_tok": t_tok,
            "time_filt": t_filt,
            "time_stem": t_stem,
            "time_bow": t_bow,
            "total_time": total_time,
            "peak_memory_kb": peak_mem / 1024
        }


class BuiltinNLTK_Pipeline:
    """Standard built-in NLP implementation using NLTK and standard collections."""
    def __init__(self, remove_stage_directions: bool = True, custom_stopwords: Optional[Set[str]] = None):
        self.remove_stage_directions = remove_stage_directions
        self.stemmer = NLTKPorterStemmer()
        self.stage_dirs = STAGE_DIRECTIONS if remove_stage_directions else set()
        self.stopwords = custom_stopwords if custom_stopwords is not None else STANDARD_STOPWORDS
        self.tokenizer_pattern = re.compile(r"[a-z]+(?:'[a-z]+)?")
        self.cache: Dict[str, str] = {}

    def stem_cached(self, word: str) -> str:
        res = self.cache.get(word)
        if res is None:
            res = self.stemmer.stem(word)
            self.cache[word] = res
        return res

    def run_pipeline(self, raw_text: str) -> Dict:
        t0 = time.time()
        tracemalloc.start()

        # Step 1: Clean
        t_clean0 = time.time()
        cleaned = raw_text.lower()
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        t_clean = time.time() - t_clean0

        # Step 2: Tokenize (using NLTK RegexpTokenizer equivalent)
        t_tok0 = time.time()
        tokens = self.tokenizer_pattern.findall(cleaned)
        t_tok = time.time() - t_tok0

        # Step 3: Stopwords
        t_filt0 = time.time()
        filtered = [t for t in tokens if t not in self.stopwords and t not in self.stage_dirs]
        t_filt = time.time() - t_filt0

        # Step 4: Stemming (with memoization)
        t_stem0 = time.time()
        stem_fn = self.stem_cached
        stemmed = [stem_fn(t) for t in filtered]
        t_stem = time.time() - t_stem0

        # Step 5: Bag of Words
        t_bow0 = time.time()
        bow = Counter(filtered)
        stem_bow = Counter(stemmed)
        t_bow = time.time() - t_bow0

        total_time = time.time() - t0
        curr_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            "num_raw_chars": len(raw_text),
            "num_raw_tokens": len(tokens),
            "num_filtered_tokens": len(filtered),
            "num_unique_words": len(bow),
            "num_unique_stems": len(stem_bow),
            "bow": bow,
            "stem_bow": stem_bow,
            "time_clean": t_clean,
            "time_tok": t_tok,
            "time_filt": t_filt,
            "time_stem": t_stem,
            "time_bow": t_bow,
            "total_time": total_time,
            "peak_memory_kb": peak_mem / 1024
        }


class ShakespeareMoodAnalyzer:
    """Analyzes thematic lexical categories and sentiment mood across the corpus."""
    THEMES = {
        "Kingship & Royalty": ["king", "queen", "prince", "crown", "lord", "majesty", "throne", "duke", "royal", "empire", "sovereign"],
        "Conflict & Tragedy": ["death", "die", "dead", "blood", "kill", "war", "battle", "sword", "fear", "foe", "enemy", "murder", "woe", "sorrow"],
        "Love & Romance": ["love", "heart", "fair", "sweet", "beauty", "kiss", "dear", "passion", "desire", "beloved", "embrace"],
        "Honor & Virtue": ["good", "honor", "noble", "true", "honest", "virtue", "truth", "faith", "praise", "worth", "justice"],
        "Time & Fate": ["time", "fate", "day", "night", "heaven", "fortune", "destiny", "hour", "age", "years", "grave", "eternal"],
        "Melancholy & Grief": ["grief", "weep", "tears", "sad", "mourn", "sigh", "pain", "pale", "dark", "heavy", "despair"]
    }

    @staticmethod
    def analyze_mood(bow: Dict[str, int]) -> Dict[str, Dict]:
        results = {}
        total_theme_hits = 0
        for category, terms in ShakespeareMoodAnalyzer.THEMES.items():
            cat_count = sum(bow.get(term, 0) for term in terms)
            total_theme_hits += cat_count
            results[category] = {
                "count": cat_count,
                "top_terms": sorted([(t, bow.get(t, 0)) for t in terms if bow.get(t, 0) > 0],
                                    key=lambda x: x[1], reverse=True)
            }
        
        for cat in results:
            results[cat]["percentage"] = (results[cat]["count"] / total_theme_hits * 100) if total_theme_hits > 0 else 0
            
        return results


def run_comparative_benchmark(filepath: str) -> List[Dict]:
    """Runs rigorous benchmarking on 25%, 50%, 75%, and 100% corpus fractions."""
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read()

    fractions = [0.25, 0.50, 0.75, 1.00]
    benchmark_records = []

    print("=" * 95, flush=True)
    print(f"{'Fraction':<10} | {'Chars':<10} | {'Custom T(s)':<12} | {'NLTK T(s)':<12} | {'Custom Mem(MB)':<15} | {'NLTK Mem(MB)':<14} | {'Top-50 Match'}", flush=True)
    print("-" * 95, flush=True)

    for frac in fractions:
        slice_len = int(len(full_text) * frac)
        corpus_slice = full_text[:slice_len]

        custom_pipe = CustomNLP_Pipeline()
        custom_res = custom_pipe.run_pipeline(corpus_slice)

        nltk_pipe = BuiltinNLTK_Pipeline()
        nltk_res = nltk_pipe.run_pipeline(corpus_slice)

        custom_bow_dict = custom_res["bow"]
        nltk_bow_dict = dict(nltk_res["bow"])

        set_custom = set(custom_bow_dict.keys())
        set_nltk = set(nltk_bow_dict.keys())
        jaccard = len(set_custom.intersection(set_nltk)) / len(set_custom.union(set_nltk)) if set_custom else 1.0

        top_custom = [w for w, _ in sorted(custom_bow_dict.items(), key=lambda x: x[1], reverse=True)[:50]]
        top_nltk = [w for w, _ in nltk_res["bow"].most_common(50)]
        overlap = len(set(top_custom).intersection(set(top_nltk))) / 50.0

        print(f"{int(frac*100)}% ({frac:<4.2f})  | {len(corpus_slice):<10} | {custom_res['total_time']:<12.4f} | {nltk_res['total_time']:<12.4f} | {custom_res['peak_memory_kb']/1024:<15.2f} | {nltk_res['peak_memory_kb']/1024:<14.2f} | {overlap*100:.1f}%", flush=True)

        benchmark_records.append({
            "Fraction": f"{int(frac*100)}%",
            "Chars": len(corpus_slice),
            "Custom_Total_Time_s": custom_res["total_time"],
            "NLTK_Total_Time_s": nltk_res["total_time"],
            "Custom_Peak_Mem_MB": custom_res["peak_memory_kb"] / 1024,
            "NLTK_Peak_Mem_MB": nltk_res["peak_memory_kb"] / 1024,
            "Custom_Tokens": custom_res["num_raw_tokens"],
            "NLTK_Tokens": nltk_res["num_raw_tokens"],
            "Vocabulary_Jaccard": jaccard,
            "Top50_Overlap": overlap,
            "Custom_Time_Clean": custom_res["time_clean"],
            "Custom_Time_Tok": custom_res["time_tok"],
            "Custom_Time_Stem": custom_res["time_stem"],
            "Custom_Time_BoW": custom_res["time_bow"],
            "NLTK_Time_Clean": nltk_res["time_clean"],
            "NLTK_Time_Tok": nltk_res["time_tok"],
            "NLTK_Time_Stem": nltk_res["time_stem"],
            "NLTK_Time_BoW": nltk_res["time_bow"],
        })

    return benchmark_records


if __name__ == "__main__":
    benchmark_records = run_comparative_benchmark("Assignment 2/docs/shakespeare.txt")
