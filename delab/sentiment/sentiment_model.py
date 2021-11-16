import os
from trax import layers as tl

from delab.nlp_util import process_tweet

TASK_DESCRIPTION = "sentiment analysis"


def classifier(vocab_size, embedding_dim=256, output_dim=2, mode='train'):
    """
    home brew sentiment classfier with trax
    after renaming a folder from data -> to something else there might be a bug somewhere
    :param vocab_size:
    :param embedding_dim:
    :param output_dim:
    :param mode:
    :return:
    """
    # create embedding layer
    embed_layer = tl.Embedding(
        vocab_size=vocab_size,  # Size of the vocabulary
        d_feature=embedding_dim)  # Embedding dimension

    # Create a mean layer, to create an "average" word embedding
    mean_layer = tl.Mean(axis=1)

    # Create a dense layer, one unit for each output
    dense_output_layer = tl.Dense(n_units=output_dim)

    # Create the log softmax layer (no parameters needed)
    log_softmax_layer = tl.LogSoftmax()

    # Use tl.Serial to combine all layers
    # and create the classifier
    # of type trax.layers.combinators.Serial
    model = tl.Serial(
        embed_layer,  # embedding layer
        mean_layer,  # mean layer
        dense_output_layer,  # dense output layer
        log_softmax_layer  # log softmax layer
    )
    # return the model of type
    return model


def get_model_path():
    # output_dir = os.getcwd() + '/model/'
    output_dir = "model/"
    # output_dir_expand = os.path.expanduser(output_dir)
    print("using as trained sentiment model path {}".format(output_dir))
    return output_dir


def tweet_to_tensor(tweet, vocab_dict, unk_token='__UNK__', verbose=False):
    """
    Input:
        tweet - A string containing a tweet
        vocab_dict - The words dictionary
        unk_token - The special string for unknown tokens
        verbose - Print info durign runtime
    Output:
        tensor_l - A python list with

    """

    # Process the tweet into a list of words
    # where only important words are kept (stop words removed)
    word_l = process_tweet(tweet)

    if verbose:
        print("List of words from the processed tweet:")
        print(word_l)

    # Initialize the list that will contain the unique integer IDs of each word
    tensor_l = []

    # Get the unique integer ID of the __UNK__ token
    unk_ID = vocab_dict[unk_token]

    if verbose:
        print(f"The unique integer ID for the unk_token is {unk_ID}")

    # for each word in the list:
    for word in word_l:
        # Get the unique integer ID.
        # If the word doesn't exist in the vocab dictionary,
        # use the unique ID for __UNK__ instead.
        word_ID = vocab_dict.get(word, unk_ID)

        # Append the unique integer ID to the tensor list.
        tensor_l.append(word_ID)

    return tensor_l
