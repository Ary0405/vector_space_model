from collections import defaultdict
import math
import os


def readDocuments(folderName):
    documents = defaultdict(list)
    try:
        for filename in os.listdir(folderName):
            with open(folderName + "/" + filename, "r") as file:
                text = file.read()
                text_tokens = text.lower().split()
                documents[filename] = text_tokens
    except Exception as e:
        print(f"Error reading documents: {e}")
    return documents


def findUniqueWords(documents):
    unique_words = set()
    try:
        for document in documents.values():
            for word in document:
                unique_words.add(word)
    except Exception as e:
        print(f"Error finding unique words: {e}")
    return unique_words


def calculatetfWeight(tf):
    return (1 + math.log10(tf))


def calculateidfWeight(df, N):
    return math.log10(N / df)


def createPostingList(documents, unique_words):
    posting_list = {}
    # Calculating document frequencies
    document_frequencies = defaultdict(int)
    for word in unique_words:
        for text_tokens in documents.values():
            if word in text_tokens:
                document_frequencies[word] += 1

    # Building the posting list
    for word in unique_words:
        posting_list[(word, document_frequencies[word])] = []
        for doc_name, text_tokens in documents.items():
            term_freq = text_tokens.count(word)
            if term_freq > 0:
                posting_list[(word, document_frequencies[word])].append(
                    (doc_name, calculatetfWeight(term_freq))
                )


    return posting_list


def main():
    folderName = "Corpus"
    try:
        documents = readDocuments(folderName)
        unique_words = findUniqueWords(documents)
        posting_list = createPostingList(documents, unique_words)

        # want to print this posting list in a text file in a readable format
        with open("posting_list.txt", "w") as file:
            for key, value in posting_list.items():
                file.write(f"{key}: {value}\n")
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
