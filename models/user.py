#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime

from models import Base, DBSession


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False, unique=True)
    last_login_time = Column(DateTime)
    last_online_time = Column(DateTime)
    register_time = Column(DateTime, nullable=False)


def add_user(student_code):
    session = DBSession()
    user = User()
    user.student_code = student_code
    user.register_time = datetime.datetime.now()
    session.add(user)
    session.commit()


def modify_user(student_code, last_login_time, last_online_time):
    session = DBSession()
    user = session.query(User).filter(User.student_code == student_code).first()
    if last_login_time:
        user.last_login_time = last_login_time
    if last_online_time:
        user.last_online_time = last_online_time
    session.commit()


if __name__ == '__main__':
    add_user('31702411')
