# Alexandra Brown, Gabriel Hodge, Noriyuki Kojima, Harry Zhang
# EECS 486 Final Project - W17
# Lyrical Genre Predictor

import sys
from vectorization import *
from naive_bayes import *
from rocchio import *
from knn import *
from cluster import *
from database import *
from sklearn.metrics import *
from svm import *
from lyrics_to_bow import *
# from NN.neural_network import * #  computation intensive

usage_string = '''python3 main.py [tf_idf | count | binary | lsa]
                  [naive_bayes | rocchio | knn | svm | kmeans |
                  agglomerative | spectral | neural_network]
                  <optional_filename>'''
num_training_tracks = 1000
num_testing_tracks = 100


def main():
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Error! USAGE: " + usage_string)
        sys.exit(1)

    vect_opts = sys.argv[1]
    classifier_opts = sys.argv[2]

    vectorization_methods = ['tf_idf', 'count', 'binary', 'lsa']
    classification_schemes = ['naive_bayes', 'rocchio', 'knn', 'svm',
                              'kmeans', 'agglomerative', 'spectral',
                              'neural_network']

    if vect_opts not in vectorization_methods or classifier_opts not in classification_schemes:
        print("Error! USAGE: " + usage_string)
        sys.exit(1)

    if vect_opts == "lsa" and classifier_opts == "naive_bayes":
        print("Error! LSA and Naive Bayes do not work together!")
        sys.exit(1)

    filename = None

    # Optional filename as input for lyrics
    if len(sys.argv) == 4:
        filename = sys.argv[3]

    predicted_test_categories, test_truth = classify_songs(classifier_opts,
                                                           vect_opts, filename)

    # Only perform evaluation on tracks where the genre is known
    # If they're coming from the user, they could be anything
    if not filename:
        evaluation(predicted_test_categories, test_truth)


# Based on the options, run a classifier on song lyrics
def classify_songs(classifier_opts, vect_opts, filename):

    """
    Load the IDs
    """
    category_counts = {"Pop": 0, "Rock": 0, "Country": 0,
                       "Blues": 0, "Rap": 0}
    test_counts = {"Pop": 0, "Rock": 0, "Country": 0,
                   "Blues": 0, "Rap": 0}

    train_truth = []
    test_truth = []

    train_IDs = []
    test_IDs = []
    test_songs = []

    # Go thru the track list and set aside tracks for training and testing
    with open("songs_input.txt") as f:
        for line in f:
            try:
                # max split once
                track, category, songinfo = line.strip().split("<sep>", 2)
            except:
                print("Line error", line)
                exit(1)

            # Make sure we have enough training data
            if category_counts[category] < num_training_tracks:
                train_truth.append(category)
                train_IDs.append(track)
                category_counts[category] += 1

            # If reading from the database and we haven't
            # reached our testing quota for tracks
            elif not filename and test_counts[category] < num_testing_tracks:
                    test_truth.append(category)
                    test_IDs.append(track)
                    test_counts[category] += 1
                    test_songs.append(songinfo)

            else:

                # Reading from user specified file
                if filename:
                    if min(category_counts.values()) == num_training_tracks:
                        break
                if min(test_counts.values()) == num_testing_tracks:
                    break

    # If reading from DB
    if not filename:
        print("Testing data: ", test_counts)
        test_lyrics = get_track_list(test_IDs)

    # Reading from user file
    else:
        test_lyrics = read_file(filename)

    print("Training data: ", category_counts)
    train_lyrics = get_track_list(train_IDs)

    # vectorize train and test
    train_matrix, test_matrix = vectorization(train_lyrics, test_lyrics,
                                              vect_opts)

    # classify based on classifier_opts
    if classifier_opts == "naive_bayes":
        predicted_test_categories = naive_bayes_classifier(train_matrix,
                                                           test_matrix,
                                                           train_truth)
    elif classifier_opts == "rocchio":
        predicted_test_categories = rocchio_classifier(train_matrix,
                                                       test_matrix,
                                                       train_truth)
    elif classifier_opts == "knn":
        predicted_test_categories = knn_classifier(train_matrix,
                                                   test_matrix,
                                                   train_truth)
    elif classifier_opts == "svm":
        predicted_test_categories = svm(train_matrix, test_matrix, train_truth)

    elif classifier_opts == "kmeans":
        predicted_test_categories = kmeans(train_matrix, test_matrix,
                                           train_truth)

    elif classifier_opts == "agglomerative":
        predicted_test_categories = agglomerative(train_matrix, test_matrix,
                                                  train_truth)

    elif classifier_opts == "spectral":
        predicted_test_categories = spectral(train_matrix, test_matrix,
                                             train_truth)

    elif classifier_opts == "neural_network":
        predicted_test_categories = neural_network(train_matrix,
                                                   test_matrix, train_truth)

    else:
        print("Unrecognized classification")
        print("Error! USAGE: " + usage_string)
        sys.exit(1)

    # If user inputted file, output predictions to the terminal
    if filename:
        print("Predicted", predicted_test_categories)

    # Dictionary to keep track of accuracies for each genre
    accuracy_dict = {"Pop": 0, "Rock": 0, "Country": 0, "Blues": 0, "Rap": 0}

    if not filename:
        with open("predictions_output.txt", "w") as f:
            f.write("#trackid\tgenre\tprediction\tsong info\n")
            for id, truth, predict, songinfo in zip(test_IDs, test_truth,
                                                    predicted_test_categories,
                                                    test_songs):
                f.write("%s %s %s\t%s\n" % (id, truth, predict, songinfo))
                if truth == predict:
                    accuracy_dict[truth] += 1
        print("Accuracy for genres", accuracy_dict)

    return predicted_test_categories, test_truth


# Use data from filename as test data for the system
# Each song should be on its own line
def read_file(filename):
    test_lyrics = []
    with open(filename) as test_file:
        for track in test_file:
            bow = lyrics_to_bow(track)
            lyrics = []
            for word, count in bow.items():
                # only use words in the lyrics database
                if word_present(word):
                    lyrics.extend([word for i in range(count)])
            lyrics = " ".join(lyrics)
            if not lyrics:
                print("At least one line in the input file has no words in the indexed database.")
                sys.exit(1)
            test_lyrics.append(lyrics)
    return test_lyrics


# Evaluate based on the true categories and the predicted categories
def evaluation(predicted_test_categories, test_truth):
    num_correct = 0
    for i in range(len(test_truth)):
        if predicted_test_categories[i] == test_truth[i]:
            num_correct += 1
    print("Correctly predicted " + str(num_correct) + " out of " + str(len(test_truth)))

    microP = precision_score(test_truth, predicted_test_categories, average='micro')
    print("Micro precision ", microP)
    macroP = precision_score(test_truth, predicted_test_categories, average='macro')
    print("Macro precision ", macroP)

    microR = recall_score(test_truth, predicted_test_categories, average='micro') 
    print("Micro recall ", microR)
    macroR = recall_score(test_truth, predicted_test_categories, average='macro')
    print("Macro recall ", macroR)

    f1 = f1_score(test_truth, predicted_test_categories, average='micro')
    print("Micro F1 Score ", f1)
    f1 = f1_score(test_truth, predicted_test_categories, average='macro')
    print("Macro F1 Score ", f1)


if __name__ == "__main__":
    main()
