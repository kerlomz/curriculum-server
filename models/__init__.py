#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine('mysql+pymysql://root:Taoting990718@newitd-w.mysql.rds.aliyuncs.com:3306/curriculum')

DBSession = sessionmaker(bind=engine)
