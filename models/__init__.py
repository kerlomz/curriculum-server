#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

Base = declarative_base(metadata=metadata)

engine = create_engine('mysql+pymysql://root:Taoting990718@newitd-w.mysql.rds.aliyuncs.com:3306/curriculum')


DBSession = sessionmaker(bind=engine)

@contextmanager
def session_maker(session=DBSession()):
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
