# the idea of this file is that it is annoying to rewrite the sql commands depending on the context you are running
# which could be django or jupyter in our case

import importlib
import sqlite3

import pandas as pd
from IPython import get_ipython
from django_pandas.io import read_frame


def query_sql(app="delab",
              table_name="tweet",
              fieldnames=["id", "conversation_id", "author_id", "created_at", "in_reply_to_user_id", "text"]):
    if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
        pd.set_option('display.max_colwidth', None)  # I am settings this here for easy of use currently

        cnx = sqlite3.connect('db.sqlite3')
        fields_string = ", ".join(fieldnames)
        table_string = app + "_" + table_name
        df = pd.read_sql_query(
            "SELECT " +
            fields_string +
            "  FROM " +
            table_string,
            cnx)
    else:
        module_name = app + ".models"
        module = importlib.import_module(module_name)
        class_name = get_class_mapping(table_name)
        class_ = getattr(module, class_name)
        instance = class_()
        qs = class_.objects.all()
        df = read_frame(qs, fieldnames=fieldnames)
    return df


def get_class_mapping(table_name):
    mapping = {"tweet": "Tweet"}
    if table_name not in mapping:
        raise Exception("table name not in get_class_mapping")
    else:
        return mapping.get(table_name)
