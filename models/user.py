#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime

from models import Base, DBSession
from models.heartbeat import get_people_number


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False, unique=True)
    last_login_time = Column(DateTime)
    last_online_time = Column(DateTime)
    base_delay_time = Column(Integer)
    extra_delay_time = Column(Integer)
    register_time = Column(DateTime, nullable=False)


def add_user(student_code):
    session = DBSession()
    user = User()
    user.student_code = student_code
    user.register_time = datetime.datetime.now()
    session.add(user)
    session.commit()
    return user


def modify_user(student_code, last_login_time, last_online_time):
    session = DBSession()
    user = session.query(User).filter(User.student_code == student_code).first()
    if not user:
        user = add_user(student_code)

    if last_login_time:
        user.last_login_time = last_login_time
    if last_online_time:
        user.last_online_time = last_online_time
    session.commit()


def get_delay_time(student_code, course):
    session = DBSession()
    user = session.query(User).filter(User.student_code == student_code).first()
    base_delay_time = user.base_delay_time if user.base_delay_time else 100
    extra_delay_time = user.extra_delay_time if user.extra_delay_time else 100
    delay_time = base_delay_time + extra_delay_time * get_people_number(course)
    return delay_time


if __name__ == '__main__':
    add_user('31702411')
