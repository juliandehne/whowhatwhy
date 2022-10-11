# bertopiclocation
import logging

from delab.delab_enums import LANGUAGE

BERTOPIC_MODEL_LOCATION = "bertopic_models/BERTopic"

logger = logging.getLogger(__name__)


def get_bertopic_location(language, version, topic=None):
    if topic is not None:
        return BERTOPIC_MODEL_LOCATION + "_" + topic + "_" + language + "_" + version
    return BERTOPIC_MODEL_LOCATION + "_" + language + "_" + version


def get_embedding_model(language):
    """
    the embedding models should be downloaded from huggingface sentence transformer store
    :param language:
    :return:
    """
    if language == LANGUAGE.GERMAN:
        # return "sentence-transformers/distiluse-base-multilingual-cased-v2"
        # return "distiluse-base-multilingual-cased-v2"
        return "german-roberta-sentence-transformer-v2"
    return "all-mpnet-base-v2"

    # comment these in for downloading the embeddings dynamically
    # return "sentence-transformers/all-mpnet-base-v2"
