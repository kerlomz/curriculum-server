#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime
from models import Base, session_maker, engine
from models.heartbeat import Heartbeat
from entity import ClientMessage


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False, unique=True)
    last_login_device = Column(String(100))
    last_login_auth_license = Column(String(100))
    last_login_time = Column(DateTime)
    last_online_time = Column(DateTime)
    base_delay_time = Column(Integer)
    extra_delay_time = Column(Integer)
    registered_time = Column(DateTime, nullable=False)

    @classmethod
    def add(cls, student_code, device_id):
        with session_maker() as session:
            user = cls()
            user.student_code = student_code
            user.last_login_device = device_id
            user.registered_time = datetime.datetime.now()
            session.add(user)
        return user

    @classmethod
    def modify(cls, client_msg: ClientMessage, last_login_time=None, last_online_time=None):
        with session_maker() as session:
            user = session.query(User).filter(User.student_code == client_msg.student_code).first()
            if not user:
                user = User.add(client_msg.student_code, client_msg.device.device_id)

            user.last_login_auth_license = client_msg.auth_license
            user.last_login_device = client_msg.device.device_id
            if last_login_time:
                user.last_login_time = last_login_time
            if last_online_time:
                user.last_online_time = last_online_time

    @classmethod
    def get_delay_time(cls, student_code, course):
        with session_maker() as session:
            user = session.query(User).filter(User.student_code == student_code).first()
            base_delay_time = user.base_delay_time if user.base_delay_time else 100
            extra_delay_time = user.extra_delay_time if user.extra_delay_time else 100
            delay_time = base_delay_time + extra_delay_time * Heartbeat.get_people_number(course)
        return delay_time


if __name__ == '__main__':
    User.metadata.drop_all(engine)
    User.metadata.create_all(engine)

    User.add('31702411', '78978998')
    a = User.get_delay_time("31702411", "78978998")
    print(a)
