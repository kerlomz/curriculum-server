#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime

from models import Base, DBSession


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    last_login_time = Column(DateTime)
    create_time = Column(DateTime, nullable=False)


def add_user(student_code):
    session = DBSession()

    user = User()
    user.student_code = student_code
    user.create_time = datetime.datetime.now()

    session.add(user)
    session.commit()


if __name__ == '__main__':
    add_user('31702411')
