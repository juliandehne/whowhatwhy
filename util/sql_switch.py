# the idea of this file is that it is annoying to rewrite the sql commands depending on the context you are running
# which could be django or jupyter in our case

import importlib
import logging
import os
import sqlite3

import pandas as pd
from IPython import get_ipython
from django.db.utils import ProgrammingError
from django_pandas.io import read_frame
import psycopg2 as pg


def query_sql(app="delab",
              table_name="tweet",
              fieldnames=None):
    fieldnames = get_standard_field_names(fieldnames)
    if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
        pd.set_option('display.max_colwidth', None)  # I am settings this here for easy of use currently
        default_database = os.getenv('DJANGO_DATABASE', 'postgres_local')
        if default_database == "postgres_local":
            cnx = create_postgres_cnx()
        else:
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
        try:
            qs = class_.objects.all()
            df = read_frame(qs, fieldnames=fieldnames)
        except ProgrammingError:
            logging.error("tried to get query_set but gave error")
            return class_.objects.none()
    return df


def get_query_native(query_string, app="delab",
                     fieldnames=None,
                     table_name="tweet"):
    fieldnames = get_standard_field_names(fieldnames)
    if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
        pd.set_option('display.max_colwidth', None)  # I am settings this here for easy of use currently
        default_database = os.getenv('DJANGO_DATABASE', 'postgres_local')
        if default_database == "postgres_local":
            cnx = create_postgres_cnx()
        else:
            print("using sqlile")
            cnx = sqlite3.connect('db.sqlite3')
        return pd.read_sql_query(query_string, cnx)
    else:
        print("running in django context")
        module_name = app + ".models"
        module = importlib.import_module(module_name)
        class_name = get_class_mapping(table_name)
        class_ = getattr(module, class_name)
        instance = class_()
        try:
            qs = class_.objects.raw(query_string).all()
            df = read_frame(qs, fieldnames=fieldnames)
        except ProgrammingError:
            logging.error("tried to get query_set but gave error")
            return class_.objects.none()


def create_postgres_cnx():
    print("using postgres")
    cnx = pg.connect(user="postgres",
                     password="postgres",
                     host="127.0.0.1",
                     port="5432",
                     database="postgres")
    return cnx


def get_standard_field_names(fieldnames):
    if fieldnames is None:
        fieldnames = ["id", "conversation_id", "author_id", "created_at", "in_reply_to_user_id", "text",
                      "bertopic_id"]
    return fieldnames


def get_class_mapping(table_name):
    mapping = {"tweet": "Tweet"}
    if table_name not in mapping:
        raise Exception("table name not in get_class_mapping")
    else:
        return mapping.get(table_name)
