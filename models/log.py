#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime

from models import Base, DBSession


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    info = Column(String(1000), nullable=False)
    create_time = Column(DateTime, nullable=False)


def add_log(student_code, info):
    session = DBSession()

    log = Log()
    log.student_code = student_code
    log.log = info
    log.create_time = datetime.datetime.now()

    session.add(log)
    session.commit()


if __name__ == '__main__':
    add_log('31702411', '111')
