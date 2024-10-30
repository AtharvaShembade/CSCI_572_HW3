import re
import os
from collections import defaultdict
from functools import reduce

# Regex to match any character that is not a word or whitespace
WORD_RE = re.compile(r'[^\w\s]')

def preprocess(text):
    """Clean and lowercase the text."""
    text = WORD_RE.sub(' ', text)  # Remove punctuation
    text = re.sub(r'\d+', ' ', text)  # Remove numbers
    return text.lower().strip()

def get_file_paths(folder_path):
    """Retrieve all text files from the specified folder."""
    file_paths = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_paths.append(os.path.join(folder_path, filename))
    return file_paths

def file_to_term_counts(file_path):
    """Map function to process a single file and return unigram and bigram counts."""
    term_counts = defaultdict(lambda: defaultdict(int))  # term_counts[term][doc_id] = count

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split('\t', 1)
            if len(parts) < 2:
                continue
            doc_id, content = parts[0].strip(), parts[1].strip()
            
            # Preprocess content and split into words
            words = preprocess(content).split()
            
            # Count unigrams
            for word in words:
                term_counts[f"unigram:{word}"][doc_id] += 1
    return term_counts

def combine_counts(count1, count2):
    """Reduce function to combine two term count dictionaries."""
    for term, doc_counts in count2.items():
        if term in count1:
            for doc_id, count in doc_counts.items():
                count1[term][doc_id] += count
        else:
            count1[term] = doc_counts
    return count1

def reducer(term_counts):
    """Function to write the aggregated counts to output files."""
    with open("unigram_index.txt", "w") as unigram_file:
        for term, doc_counts in term_counts.items():
            # Format each term with its document IDs and counts
            doc_counts_str = ' '.join([f"{doc_id}:{count}" for doc_id, count in doc_counts.items()])
            
            # Write unigrams and bigrams to respective files
            if term.startswith("unigram:"):
                unigram_file.write(f"{term[8:]}\t{doc_counts_str}\n")

if __name__ == "__main__":
    # Specify the folder containing the text files
    folder_path = ''

    # Get all file paths from the folder
    input_files = get_file_paths(folder_path)

    # Map step: Process each file to get individual term counts
    mapped_counts = map(file_to_term_counts, input_files)

    # Reduce step: Combine all individual dictionaries into one
    total_counts = reduce(combine_counts, mapped_counts)

    # Write the final aggregated counts to output files
    reducer(total_counts)
