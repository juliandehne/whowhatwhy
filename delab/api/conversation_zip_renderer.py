"""
In this file we bundle the methods used for exporting our current data as a zip file

"""
import io
import zipfile

import requests
from django.http import HttpResponse

from django_project.settings import INTERNAL_IPS
from .api_util import get_file_name, get_all_conversation_ids


def create_zip_response_conversation(request, topic, conversation_id, filename):
    # Create zip

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    download_conversations_in_all_formats(conversation_id, request, topic, zip_file, "both")

    zip_file.close()

    # Return zip
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response


def download_conversations_in_all_formats(conversation_id, request, topic, zip_file, full):
    full_string = "full"
    full_cropped_string = "cropped"
    server_adress = "http://" + INTERNAL_IPS[0] + ":" + request.META['SERVER_PORT']
    file_type_text = "tweets_text"

    """
    if full == "cropped" or full == "both":
        cropped_response = get_file_from_rest(conversation_id, file_type_text, full_cropped_string, server_adress,
                                              topic)
        zip_file.writestr(get_file_name(conversation_id, full_cropped_string, ".txt"), cropped_response.content)
        cropped_response = get_file_from_rest(conversation_id, "tweets_excel", full_cropped_string, server_adress,
                                              topic)
        zip_file.writestr(get_file_name(conversation_id, full_cropped_string, ".xlsx"), cropped_response.content)

        # cropped_response = get_file_from_rest(conversation_id, "tweets_json", full_cropped_string, server_adress, topic)
        # zip_file.writestr(get_file_name(conversation_id, full_cropped_string, ".json"), cropped_response.content)
    """
    if full == "full" or full == "both":
        cropped_response = get_file_from_rest(conversation_id, "tweets_json", full_string, server_adress, topic)
        zip_file.writestr(get_file_name(conversation_id, full_string, ".json"), cropped_response.content)
        cropped_response = get_file_from_rest(conversation_id, file_type_text, full_string, server_adress, topic)
        zip_file.writestr(get_file_name(conversation_id, full_string, ".txt"), cropped_response.content)
        cropped_response = get_file_from_rest(conversation_id, "tweets_excel", full_string, server_adress, topic)
        zip_file.writestr(get_file_name(conversation_id, full_string, ".xlsx"), cropped_response.content)


def get_file_from_rest(conversation_id, file_type, full, server_address, topic):
    txt_cropped_url = "{}/delab/rest/{}/{}/conversation/{}/{}".format(server_address,
                                                                      topic,
                                                                      file_type,
                                                                      str(conversation_id),
                                                                      full)
    if file_type == "tweets_json":
        txt_cropped_url += "?format=json"
    # Get file
    cropped_response = requests.get(txt_cropped_url)
    # cropped_response
    return cropped_response


def create_full_zip_response_conversation(request, topic, filename, full):
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    conversation_ids = get_all_conversation_ids(topic)[:5]
    for conversation_id in conversation_ids:
        download_conversations_in_all_formats(conversation_id, request, topic, zip_file, full)
    zip_file.close()

    # Return zip
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response
