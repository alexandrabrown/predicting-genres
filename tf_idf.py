import sys
from sklearn.feature_extraction.text import TfidfVectorizer


def tf_idf_vectorize(train_lyrics, test_lyrics, option):
    """
    TF-IDF vectorizer
    Input: two lists of strings and one option
    Output: If "dense" is set, two dense matrices (training and testing)
            If "sparse" is set, one sparse matrix,
            the length of training, and the length of testing
    Example: tf_idf_vectorize(train_lyrics, test_lyrics, "sparse")
             tf_idf_vectorize(train_lyrics, test_lyrics, "dense")
    """
    corpus = train_lyrics + test_lyrics

    vectorizer = TfidfVectorizer(min_df=1)

    if option == "dense":
        dmatrix = vectorizer.fit_transform(corpus).toarray()
        assert(len(dmatrix) == len(train_lyrics) + len(test_lyrics))
        return dmatrix[:len(train_lyrics)], dmatrix[-len(test_lyrics):]
    elif option == "sparse":
        return vectorizer.fit_transform(corpus), len(train_lyrics), len(test_lyrics)
    else:
        print ("Invalid option!")
        print("Error! USAGE: " + usage_string)
        sys.exit(1)
