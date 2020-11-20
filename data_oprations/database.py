from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

sql_config_path = os.path.join(os.path.dirname(__file__),'../','../','sql_config')
with open(sql_config_path) as f:
    sql_str = f.read()

engine = create_engine(sql_str,pool_size=15,pool_recycle=60, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()