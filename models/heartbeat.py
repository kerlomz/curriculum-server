#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime

from models import Base, DBSession


class Heartbeat(Base):
    __tablename__ = 'heartbeat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    log = Column(String(1000), nullable=False)
    create_time = Column(DateTime, nullable=False)


def add_heartbeat(student_code, log):
    session = DBSession()

    heartbeat = Heartbeat()
    heartbeat.student_code = student_code
    heartbeat.log = log
    heartbeat.create_time = datetime.datetime.now()

    session.add(heartbeat)
    session.commit()


if __name__ == '__main__':
    add_heartbeat('31702411', '1111')
    pass
