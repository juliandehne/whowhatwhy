class BertopicModelMissingException(Exception):

    def __init__(self, model_name, topic, language, platform):
        self.model_name = model_name
        self.topic = topic
        self.language = language
        self.platform = platform
        self.message = "Bertopic model at location {} was not found for language:{} and platform:{} and topic:{}".format(
            model_name, topic, language, platform)
