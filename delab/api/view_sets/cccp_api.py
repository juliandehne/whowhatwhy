from django.http import Http404
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from delab.corpus.filter_conversation_trees import convert_to_conversation_trees
from delab.models import TweetAuthor
from ..api_util import get_file_name, PassthroughRenderer, TabbedTextRenderer
from ..conversation_zip_renderer import create_zip_response_cccp


@api_view(['GET'])
@renderer_classes([PassthroughRenderer])
def get_cccp_zip(request):
    return create_zip_response_cccp(request)


@api_view(['GET'])
@renderer_classes([TabbedTextRenderer])
def get_tabbed_conversation_for_central_authors_view(request, conversation_id, author_id):
    trees = convert_to_conversation_trees(conversation_id=conversation_id)
    if conversation_id in trees:
        conversation_tree = trees[conversation_id]
        if TweetAuthor.objects.filter(id=author_id).exists():
            author_string = TweetAuthor.objects.filter(id=author_id).get().name
        else:
            author_string = str(author_id)
        result = "CCCP Author is: {} \n\n\n\n".format(author_string)
        result += conversation_tree.to_string() + "\n\n"
        response = Response(result)
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format("cccp_" + get_file_name(str(conversation_id), str(author_id), ".txt")))
        return response

    else:
        raise Http404


"""
class CentralAuthorTweetSerializer(serializers.Serializer):
    tw_author__name = serializers.CharField(max_length=400)
    is_central = serializers.BooleanField()
    text = serializers.CharField(max_length=2000)
"""

"""
# ViewSets define the view behavior.
class CentralAuthorExcelViewSet(XLSXFileMixin, viewsets.ModelViewSet):
    queryset = Tweet.objects.none()
    serializer_class = CentralAuthorTweetSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'central_author.xlsx'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = tweet_fields_used

    # filterset_fields = ['conversation_id', 'tn_order', 'author_id', 'language']
    def get_queryset(self):
        conversation_id = self.kwargs["conversation_id"]
        return get_central_author_tweet_queryset(conversation_id)
"""
