#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

Base = declarative_base(metadata=metadata)

engine = create_engine('mysql+pymysql://root:Taoting990718@newitd-w.mysql.rds.aliyuncs.com:3306/curriculum',
                       pool_size=100, pool_recycle=5, pool_timeout=30, pool_pre_ping=True, max_overflow=0)

DBSession = sessionmaker(bind=engine)


@contextmanager
def session_maker():
    session = DBSession()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()
