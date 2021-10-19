from IPython import get_ipython

from util.sql_switch import query_sql


def run():
    res = get_ipython().__class__.__name__
    print(res)
    df = query_sql()
    print(df.head(3))
