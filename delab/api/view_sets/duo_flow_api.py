from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view, renderer_classes

from delab.api.api_util import PassthroughRenderer
from delab.api.flow_renderer import render_duo_flows
from delab.api.view_sets.corpus_api import TweetSerializer, TweetTextSerializer
from django_project.settings import MAX_DUO_FLOWS_FOR_ANALYSIS
from ...analytics.flow_duos import get_flow_duos, get_flow_duo_windows


class FLowDuoSerializer(serializers.Serializer):
    name1 = serializers.CharField(max_length=500)
    name2 = serializers.CharField(max_length=500)
    toxic_delta = serializers.FloatField()
    tweets1 = TweetSerializer(many=True)
    tweets2 = TweetSerializer(many=True)


class FlowDuoWindowSerialzer(serializers.Serializer):
    name1 = serializers.CharField(max_length=500)
    name2 = serializers.CharField(max_length=500)
    toxic_delta = serializers.FloatField()
    common_tweets = TweetTextSerializer(many=True)
    tweets1_post_branching = TweetTextSerializer(many=True)
    tweets2_post_branching = TweetTextSerializer(many=True)


class FlowDuoTweetSet(viewsets.ModelViewSet):
    serializer_class = FLowDuoSerializer

    def get_queryset(self):
        dual_flows = get_flow_duos(MAX_DUO_FLOWS_FOR_ANALYSIS)
        return dual_flows


class FlowDuoWindowTweetSet(viewsets.ModelViewSet):
    serializer_class = FlowDuoWindowSerialzer

    def get_queryset(self):
        result = get_flow_duo_windows()
        return result


@api_view(['GET'])
@renderer_classes([PassthroughRenderer])
def get_duo_flow_zip(request):
    return render_duo_flows()
