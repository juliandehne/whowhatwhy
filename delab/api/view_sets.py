from django.utils.encoding import smart_text
from django_filters.rest_framework import DjangoFilterBackend
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework import renderers
from rest_framework import serializers, viewsets
# Serializers define the API representation.
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from delab.corpus.filter_conversation_trees import get_conversation_trees
from delab.models import Tweet, TweetAuthor, TWCandidate
from .api_util import get_file_name, get_all_conversation_ids
from .conversation_zip_renderer import create_zip_response_conversation, create_full_zip_response_conversation

"""

LOOK at the README to see all the different endpoints implemented as a way to get the downloaded tweets
"""

tweet_fields_used = ['id', 'twitter_id', 'text', 'conversation_id', 'author_id', 'created_at',
                     'in_reply_to_user_id',
                     'sentiment_value', 'language']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetAuthor
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TWCandidate
        fields = '__all__'


class TweetSerializer(serializers.ModelSerializer):
    tw_author = AuthorSerializer()

    # tw_author__name = serializers.StringRelatedField()
    # tw_author__location = serializers.StringRelatedField()

    class Meta:
        model = Tweet
        fields = tweet_fields_used + ["tw_author"]
        # fields = tweet_fields_used + ["tw_author__name", "tw_author__location"]

    # https://www.django-rest-framework.org/api-guide/serializers/#writable-nested-representations


class TabbedTextRenderer(renderers.BaseRenderer):
    # here starts the wonky stuff
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_text(data, encoding=self.charset)


class NormXMLRenderer(renderers.BaseRenderer):
    # here starts the wonky stuff
    media_type = 'xhtml+xml'
    format = 'xml'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_text(data, encoding=self.charset)


def get_migration_query_set(topic):
    queryset = Tweet.objects.select_related("tw_author").filter(simple_request__topic__title=topic)
    return queryset


# ViewSets define the view behavior.
class TweetViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.none()
    serializer_class = TweetSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['conversation_id', 'tn_order', 'author_id', 'language']
    filterset_fields = tweet_fields_used

    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    def get_queryset(self):
        topic = self.kwargs["topic"]
        return get_migration_query_set(topic)


# ViewSets define the view behavior.
class CandidateExcelViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    queryset = TWCandidate.objects.all()
    serializer_class = CandidateSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'labeled_moderator_statements.xlsx'
    filter_backends = [DjangoFilterBackend]


# ViewSets define the view behavior.
class TweetExcelViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    queryset = Tweet.objects.none()
    serializer_class = TweetSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'twitter_migration_export.xlsx'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = tweet_fields_used

    # filterset_fields = ['conversation_id', 'tn_order', 'author_id', 'language']
    def get_queryset(self):
        topic = self.kwargs["topic"]
        return get_migration_query_set(topic)


class TweetSingleViewSet(TweetViewSet):
    queryset = Tweet.objects.none()

    def get_queryset(self):
        queryset = get_cropped_conversation_qs_modelview(self)
        # TODO find out why the text api produces more tweets then this one
        return queryset


class TweetExcelSingleViewSet(TweetExcelViewSet):
    def get_queryset(self):
        queryset = get_cropped_conversation_qs_modelview(self)
        return queryset

    def get_filename(self):
        conversation_id = self.kwargs["conversation_id"]
        full = self.kwargs["full"]
        return get_file_name(conversation_id, full, ".xlsx")


def get_cropped_conversation_qs_modelview(model_view):
    conversation_id = model_view.kwargs["conversation_id"]
    topic = model_view.kwargs["topic"]
    queryset = Tweet.objects.filter(topic__title=topic, conversation_id=conversation_id)
    if model_view.kwargs["full"] == "cropped":
        # queryset = get_cropped_tweet_set(queryset)
        pass
    return queryset


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_cropped_conversation_ids(request, topic):
    conversation_ids = get_all_conversation_ids(topic)
    result = {"suitable_conversation_ids": conversation_ids}
    return Response(result)


@api_view(['GET'])
@renderer_classes([TabbedTextRenderer])
def get_all_conversations_tabbed(request, topic):
    trees = get_conversation_trees(topic).values()
    result = ""
    for tree in trees:
        result += tree.to_string() + "\n\n"
    response = Response(result)
    response['Content-Disposition'] = ('attachment; filename={0}'.format(get_file_name("all", "full", ".txt")))
    return response


@api_view(['GET'])
@renderer_classes([TabbedTextRenderer])
def get_tabbed_conversation_view(request, topic, conversation_id, full):
    # if full == "cropped":
    # get_conversation_tree
    # conversation_trees = get_conversation_trees(topic, conversation_id=conversation_id,
    #  conversation_filter=ConversationFilter())

    conversation_trees = get_conversation_trees(topic, conversation_id=conversation_id).values()
    result = ""
    for tree in conversation_trees:
        if type(tree) is int:
            print("something went wrong converting the treees")
        else:
            result += tree.to_string() + "\n\n"
    response = Response(result)
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(get_file_name(conversation_id, full, ".txt")))
    return response


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


@api_view(['GET'])
@renderer_classes([PassthroughRenderer])
def get_zip_view(request, topic, conversation_id):
    return create_zip_response_conversation(request, topic, conversation_id,
                                            get_file_name(conversation_id, "both", ".zip"))


@api_view(['GET'])
@renderer_classes([PassthroughRenderer])
def get_full_zip_view(request, topic, full):
    return create_full_zip_response_conversation(request, topic,
                                                 get_file_name("all_conversations", full, ".zip"), full)


@api_view(['GET'])
@renderer_classes([NormXMLRenderer])
def get_xml_conversation_view(request, topic, conversation_id, full):
    # if full == "cropped":
    # get_conversation_tree
    # conversation_trees = get_conversation_trees(topic, conversation_id=conversation_id,
    #  conversation_filter=ConversationFilter())

    conversation_tree = get_conversation_trees(topic, conversation_id=conversation_id)[conversation_id]
    xml_dump = conversation_tree.to_norm_xml()
    response = Response(xml_dump)
    response['Content-Disposition'] = (
        'attachment; filename={0}'.format(get_file_name(conversation_id, full, ".xml")))
    return response
