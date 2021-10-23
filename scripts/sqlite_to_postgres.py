from sqlalchemy import create_engine, select
#from models import Base

engine_lite = create_engine('sqlite:///mydb.sqlite')
engine_cloud = create_engine('postgresql+psycopg2://USER:PW@/DBNAME?host=/cloudsql/INSTANCE')

#with engine_lite.connect() as conn_lite:
#    with engine_cloud.connect() as conn_cloud:
#        for table in Base.metadata.sorted_tables:
#            data = [dict(row) for row in conn_lite.execute(select(table.c))]
#            conn_cloud.execute(table.insert().values(data))
