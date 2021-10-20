import json

import nltk
from nltk.corpus import twitter_samples

from delab.models import SADictionary
from delab.nlp_util import process_tweet
import random as rnd
from trax import layers as tl
from trax.supervised import training
from trax.fastmath import numpy as np
from trax import optimizers
from delab.sentiment.sentiment_model import TASK_DESCRIPTION, classifier, get_model_path, tweet_to_tensor


def train_sentiment_classification():
    all_positive_tweets, all_negative_tweets = load_tweets()

    # View the total number of positive and negative tweets.
    print(f"The number of positive tweets: {len(all_positive_tweets)}")
    print(f"The number of negative tweets: {len(all_negative_tweets)}")

    # Split positive set into validation and training
    val_pos = all_positive_tweets[4000:]  # generating validation set for positive tweets
    train_pos = all_positive_tweets[:4000]  # generating training set for positive tweets

    # Split negative set into validation and training
    val_neg = all_negative_tweets[4000:]  # generating validation set for negative tweets
    train_neg = all_negative_tweets[:4000]  # generating training set for nagative tweets

    # Combine training data into one set
    train_x = train_pos + train_neg

    # Combine validation data into one set
    val_x = val_pos + val_neg

    # Set the labels for the training set (1 for positive, 0 for negative)
    train_y = np.append(np.ones(len(train_pos)), np.zeros(len(train_neg)))

    # Set the labels for the validation set (1 for positive, 0 for negative)
    val_y = np.append(np.ones(len(val_pos)), np.zeros(len(val_neg)))

    # Set the random number generator for the shuffle procedure
    rnd.seed(30)

    # Create the training data generator
    def train_generator(batch_size, shuffle=False):
        return data_generator(train_pos, train_neg, batch_size, True, vocab_dict, shuffle)

    # Create the validation data generator
    def val_generator(batch_size, shuffle=False):
        return data_generator(val_pos, val_neg, batch_size, True, vocab_dict, shuffle)

    # Create the validation corpus generator
    def test_generator(batch_size, shuffle=False):
        return data_generator(val_pos, val_neg, batch_size, False, vocab_dict, shuffle)

    vocab_dict = update_dictionary(train_x)

    batch_size = 16
    random_seed = 271
    rnd.seed(random_seed)

    train_task = training.TrainTask(
        labeled_data=train_generator(batch_size=batch_size, shuffle=True),
        loss_layer=tl.CrossEntropyLoss(),
        optimizer=optimizers.Adam(0.01),
        n_steps_per_checkpoint=10,
    )

    eval_task = training.EvalTask(
        labeled_data=val_generator(batch_size=batch_size, shuffle=True),
        metrics=[tl.CrossEntropyLoss(), tl.Accuracy()],
    )

    model = classifier(vocab_size=len(vocab_dict))

    output_dir_expand = get_model_path()
    train_model(model, train_task, eval_task, 100, output_dir_expand, random_seed=31)
    # train_model(model, train_task, eval_task, 1000, output_dir_expand, random_seed=31)
    # interestingly the model gets worse after 100 iterations

    # training_loop = train_model(model, train_task, eval_task, 100, output_dir_expand,
    # random_seed=31) model = training_loop.eval_model


def update_dictionary(tweets):
    # Build the vocabulary
    # Unit Test Note - There is no test set here only train/val
    django_dictionary_count = SADictionary.objects.filter(title=TASK_DESCRIPTION).count()
    # the dictionary is always written to the db, needs to run only once
    if django_dictionary_count > 0:
        django_dictionary = SADictionary.objects.all().filter(title=TASK_DESCRIPTION).get()
        vocab_dict = json.loads(django_dictionary.dictionary_string)
    else:
        # Include special tokens
        # started with pad, end of line and unk tokens
        vocab_dict = {'__PAD__': 0, '__</e>__': 1, '__UNK__': 2}

        # Note that we build vocab using training corpus
        for tweet in tweets:
            processed_tweet = process_tweet(tweet)
            for word in processed_tweet:
                if word not in vocab_dict:
                    vocab_dict[word] = len(vocab_dict)

        print("Total words in vocab are", len(vocab_dict))

        SADictionary.objects.all().filter(title=TASK_DESCRIPTION).delete()
        django_dictionary = SADictionary.create(json.dumps(vocab_dict), TASK_DESCRIPTION)
        django_dictionary.save()  # saving the vocabulary to db for later user
    return vocab_dict


def train_model(classifier, train_task, eval_task, n_steps, output_dir, random_seed):
    """
    Input:
        classifier - the model you are building
        train_task - Training task
        eval_task - Evaluation task
        n_steps - the evaluation steps
        output_dir - folder to save your files
    Output:
        trainer -  trax trainer
    """

    training_loop = training.Loop(
        classifier,  # The learning model
        train_task,  # The training task
        eval_tasks=[eval_task],  # The evaluation task
        output_dir=output_dir,
        random_seed=random_seed)  # The output directory

    training_loop.run(n_steps=n_steps)

    # Return the training_loop, since it has the model.
    return training_loop


def data_generator(data_pos, data_neg, batch_size, loop, vocab_dict, shuffle=False):
    """
    Input:
        data_pos - Set of positive examples
        data_neg - Set of negative examples
        batch_size - number of samples per batch. Must be even
        loop - True or False
        vocab_dict - The words dictionary
        shuffle - Shuffle the corpus order
    Yield:
        inputs - Subset of positive and negative examples
        targets - The corresponding labels for the subset
        example_weights - An array specifying the importance of each example

    """
    # make sure the batch size is an even number
    # to allow an equal number of positive and negative samples
    assert batch_size % 2 == 0

    # Number of positive examples in each batch is half of the batch size
    # same with number of negative examples in each batch
    n_to_take = batch_size // 2

    # Use pos_index to walk through the data_pos array
    # same with neg_index and data_neg
    pos_index = 0
    neg_index = 0

    len_data_pos = len(data_pos)
    len_data_neg = len(data_neg)

    # Get and array with the corpus indexes
    pos_index_lines = list(range(len_data_pos))
    neg_index_lines = list(range(len_data_neg))

    # shuffle lines if shuffle is set to True
    if shuffle:
        rnd.shuffle(pos_index_lines)
        rnd.shuffle(neg_index_lines)

    stop = False

    # Loop indefinitely
    while not stop:

        # create a batch with positive and negative examples
        batch = []

        # First part: Pack n_to_take positive examples

        # Start from pos_index and increment i up to n_to_take
        for i in range(n_to_take):

            # If the positive index goes past the positive dataset lenght,
            if pos_index >= len_data_pos:

                # If loop is set to False, break once we reach the end of the dataset
                if not loop:
                    stop = True;
                    break;

                # If user wants to keep re-using the corpus, reset the index
                pos_index = 0

                if shuffle:
                    # Shuffle the index of the positive sample
                    rnd.shuffle(pos_index_lines)

            # get the tweet as pos_index
            tweet = data_pos[pos_index_lines[pos_index]]

            # convert the tweet into tensors of integers representing the processed words
            tensor = tweet_to_tensor(tweet, vocab_dict)

            # append the tensor to the batch list
            batch.append(tensor)

            # Increment pos_index by one
            pos_index = pos_index + 1

        # Second part: Pack n_to_take negative examples

        # Using the same batch list, start from neg_index and increment i up to n_to_take
        for i in range(n_to_take):

            # If the negative index goes past the negative dataset length,
            if neg_index >= len_data_neg:

                # If loop is set to False, break once we reach the end of the dataset
                if not loop:
                    stop = True;
                    break;

                # If user wants to keep re-using the corpus, reset the index
                neg_index = 0

                if shuffle:
                    # Shuffle the index of the negative sample
                    rnd.shuffle(neg_index_lines)
            # get the tweet as neg_index
            tweet = data_neg[neg_index_lines[neg_index]]

            # convert the tweet into tensors of integers representing the processed words
            tensor = tweet_to_tensor(tweet, vocab_dict)

            # append the tensor to the batch list
            batch.append(tensor)

            # Increment neg_index by one
            neg_index = neg_index = neg_index + 1

        if stop:
            break;

        # Update the start index for positive corpus
        # so that it's n_to_take positions after the current pos_index
        pos_index += n_to_take

        # Update the start index for negative corpus
        # so that it's n_to_take positions after the current neg_index
        neg_index += n_to_take

        # Get the max tweet length (the length of the longest tweet)
        # (you will pad all shorter tweets to have this length)
        max_len = max([len(t) for t in batch])

        # Initialize the input_l, which will
        # store the padded versions of the tensors
        tensor_pad_l = []
        # Pad shorter tweets with zeros
        for tensor in batch:
            # Get the number of positions to pad for this tensor so that it will be max_len long
            n_pad = max_len - len(tensor)

            # Generate a list of zeros, with length n_pad
            pad_l = [0] * n_pad

            # concatenate the tensor and the list of padded zeros
            tensor_pad = tensor + pad_l

            # append the padded tensor to the list of padded tensors
            tensor_pad_l.append(tensor_pad)

        # convert the list of padded tensors to a numpy array
        # and store this as the model inputs
        inputs = np.array(tensor_pad_l)

        # Generate the list of targets for the positive examples (a list of ones)
        # The length is the number of positive examples in the batch
        target_pos = [1] * int(batch_size / 2)

        # Generate the list of targets for the negative examples (a list of zeros)
        # The length is the number of negative examples in the batch
        target_neg = [0] * int(batch_size / 2)

        # Concatenate the positve and negative targets
        target_l = target_pos + target_neg

        # Convert the target list into a numpy array
        targets = np.array(target_l)

        # Example weights: Treat all examples equally importantly.It should return an np.array. Hint: Use np.ones_like()
        example_weights = np.array(np.ones_like(targets))

        # note we use yield and not return
        yield inputs, targets, example_weights


# let's not reuse variables
# all_positive_tweets = twitter_samples.strings('positive_tweets.json')
# all_negative_tweets = twitter_samples.strings('negative_tweets.json')

def load_tweets():
    all_positive_tweets = twitter_samples.strings('positive_tweets.json')
    all_negative_tweets = twitter_samples.strings('negative_tweets.json')
    return all_positive_tweets, all_negative_tweets
