from bertopic import BERTopic


class TopicModelService:

    def __init__(self):

        self.model = BERTopic(
            verbose=True,
            calculate_probabilities=True
        )

    def train(self, documents):

        topics, probabilities = self.model.fit_transform(documents)

        return topics

    def topic_info(self):

        return self.model.get_topic_info()

    def get_topic(self, topic_id):

        return self.model.get_topic(topic_id)