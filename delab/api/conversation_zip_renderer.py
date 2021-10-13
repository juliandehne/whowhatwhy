"""
In this file we bundle the methods used for exporting our current corpus as a zip file

"""
import io
import urllib
import zipfile

import requests
from django.http import HttpResponse

from .api_util import get_file_name


def create_zip_response_conversation(conversation_id, filename):
    # Create zip

    full = "full"
    full_cropped = "cropped"
    server_adress = "http://127.0.0.1:8000"
    topic = "migration"

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    file_type_text = "tweets_text"
    cropped_response = get_file_from_rest(conversation_id, file_type_text, full, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full, ".txt"), cropped_response.content)

    cropped_response = get_file_from_rest(conversation_id, file_type_text, full_cropped, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full_cropped, ".txt"), cropped_response.content)

    cropped_response = get_file_from_rest(conversation_id, "tweets_excel", full, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full, ".xlsx"), cropped_response.content)

    cropped_response = get_file_from_rest(conversation_id, "tweets_excel", full_cropped, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full_cropped, ".xlsx"), cropped_response.content)

    cropped_response = get_file_from_rest(conversation_id, "tweets_json", full_cropped, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full_cropped, ".json"), cropped_response.content)

    cropped_response = get_file_from_rest(conversation_id, "tweets_json", full, server_adress, topic)
    zip_file.writestr(get_file_name(conversation_id, full, ".json"), cropped_response.content)

    zip_file.close()

    # Return zip
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response


def get_file_from_rest(conversation_id, file_type, full, server_address, topic):
    txt_cropped_url = "{}/delab/rest/{}/{}/conversation/{}/{}".format(server_address,
                                                                      topic,
                                                                      file_type,
                                                                      str(conversation_id),
                                                                      full)
    # Get file
    cropped_response = requests.get(txt_cropped_url)
    return cropped_response


def create_full_zip():
    pass
