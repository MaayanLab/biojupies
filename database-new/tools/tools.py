import os, json
import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])

data = {x: pd.read_sql_table(x, engine) for x in ['tool', 'parameter', 'parameter_value']}
