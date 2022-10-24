from rest_framework import serializers, viewsets

from delab.models import ModerationCandidate2, ModerationRating
from . import TweetSerializer


class ModerationCandidateSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = ModerationCandidate2
        fields = '__all__'


class ModerationRatingSerializer(serializers.ModelSerializer):
    mod_candidate = ModerationCandidateSerializer()

    class Meta:
        model = ModerationRating
        fields = '__all__'


class ModerationRatingTweetSet(viewsets.ModelViewSet):
    serializer_class = ModerationRatingSerializer
    queryset = ModerationRating.objects.none()

    def get_queryset(self):
        return ModerationRating.objects.select_related("mod_candidate").all()
