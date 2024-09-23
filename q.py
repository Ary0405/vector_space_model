import os
import math
from collections import defaultdict

# Step 1: Read Documents from the folder
def readDocuments(folderName):
    documents = defaultdict(list)
    try:
        for filename in os.listdir(folderName):
            with open(folderName + "/" + filename, "r", encoding="utf-8") as file:
                text = file.read()
                text_tokens = text.lower().split()
                documents[filename] = text_tokens
    except Exception as e:
        print(f"Error reading documents: {e}")
    return documents

# Step 2: Find all unique words
def findUniqueWords(documents):
    unique_words = set()
    for document in documents.values():
        for word in document:
            unique_words.add(word)
    return unique_words

# Step 3: Calculate tf Weight for documents
def calculatetfWeight(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

# Step 4: Calculate idf Weight for query
def calculateidfWeight(df, N):
    return math.log10(N / df) if df > 0 else 0

# Step 5: Create Posting List (stores log(tf) for documents)
def createPostingList(documents, unique_words):
    posting_list = {}
    document_frequencies = defaultdict(int)
    N = len(documents)

    # Calculate document frequencies
    for word in unique_words:
        for text_tokens in documents.values():
            if word in text_tokens:
                document_frequencies[word] += 1
    
    # Build the posting list
    for word in unique_words:
        posting_list[word] = []
        for doc_name, text_tokens in documents.items():
            term_freq = text_tokens.count(word)
            if term_freq > 0:
                # Store log(tf) for document
                posting_list[word].append((doc_name, calculatetfWeight(term_freq)))

    # Save the posting list to a text file in the desired format
   # Save the posting list to a text file in the desired format
    try:
        with open("postinglist.txt", "w", encoding="utf-8") as f:
            for word, postings in posting_list.items():
                df = document_frequencies[word]  # Get actual document frequency value
                # Write in the format "term", df: [(doc: "logtf"), ...]
                f.write(f'"{word}", {df}: [')
                f.write(", ".join([f'("{doc}", "{logtf:.6f}")' for doc, logtf in postings]))
                f.write("]\n")
    except Exception as e:
        print(f"Error writing to file: {e}")

                
    return posting_list, document_frequencies


# Step 6: Normalize Vectors using Cosine Normalization
def normalize_vector(vector):
    norm = math.sqrt(sum(weight ** 2 for weight in vector.values()))
    if norm == 0:
        return vector
    return {term: weight / norm for term, weight in vector.items()}

# Step 7: Compute Cosine Similarity
def compute_cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    return dot_product  # Vectors are already normalized

# Step 8: Rank documents based on cosine similarity
def rank_documents(documents, query, posting_list, document_frequencies, unique_words):
    N = len(documents)
    query_tokens = query.lower().split()
    unique_words_query = set(query_tokens)
    unique_words= unique_words.union(unique_words_query)
    query_vector = {}

    # Calculate query tf-idf weights (ltc scheme)
    for word in unique_words:
        tf = query_tokens.count(word)
        # Get df from doc_frequency based on word, default to 0 if word not found
        df = document_frequencies.get(word, 0)
        if df > 0:
            idf = calculateidfWeight(df, N) 
            query_vector[word] = calculatetfWeight(tf) * idf

    # Normalize the query vector
    query_vector = normalize_vector(query_vector)

    # Calculate cosine similarities
    similarities = {}
    for doc_name in documents.keys():
        doc_vector = {}
        for word in unique_words:
        # Get the posting list for the current word
            posting = posting_list.get(word, [])
            # Check if the document has the word
        
            for doc, log_tf in posting:
                if doc == doc_name:
                # Set idf = 1 for documents in lnc scheme
                    doc_vector[word] = log_tf * 1  # Assign the log_tf value
        
            #If the word is not found, you can explicitly set its value to 0
            if word not in doc_vector:
                doc_vector[word] = 0

        # Normalize the document vector
        doc_vector = normalize_vector(doc_vector)

        # Compute cosine similarity
        similarity = compute_cosine_similarity(query_vector, doc_vector)
        similarities[doc_name] = similarity

    # Sort documents by similarity and return top 10
    ranked_docs = sorted(similarities.items(), key=lambda item: (-item[1], item[0]))
    return ranked_docs[:10]

# Main function to put everything together
def main():
    folderName = "Corpus"
    query = "Developing your Zomato business account and profile is a great way to boost your restaurant’s online reputation"
    # Read documents and create posting list
    documents = readDocuments(folderName)
    unique_words = findUniqueWords(documents)
    posting_list, document_frequencies = createPostingList(documents, unique_words)
    # Rank documents by cosine similarity
    ranked_docs = rank_documents(documents, query, posting_list, document_frequencies, unique_words)

    print("Ranked Documents by Relevance:")
    for doc_name, score in ranked_docs:
        print(f"{doc_name}: {score:.4f}")

if __name__ == "__main__":
    main()
