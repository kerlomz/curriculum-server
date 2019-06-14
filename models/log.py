#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>
import json
import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text, Float

from models import Base, session_maker, engine
from entity import Device, ClientMessage, Context


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    content = Column(String(100), nullable=True)
    message = Column(String(2048), nullable=True)
    body = Column(Text, nullable=True)
    device_id = Column(String(128), nullable=True)
    device = Column(String(512), nullable=True)
    msg_sign = Column(String(100), nullable=True)
    msg_type = Column(String(64), nullable=False)
    msg_timestamp = Column(Float, nullable=False, default=0)
    created_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Log(id='%s', student_code='%s', content='%s', message='%s', body='%s', device_id='%s', device='%s', msg_sign='%s', msg_type='%s', msg_timestamp='%s', created_time='%s')>" % (
            self.id,
            self.student_code,
            self.content,
            self.message,
            self.body,
            self.device_id,
            self.device,
            self.msg_sign,
            self.msg_type,
            self.msg_timestamp,
            self.created_time
        )

    @classmethod
    def add(cls, client_msg: ClientMessage, content=None):

        with session_maker() as session:
            log = cls()
            log.student_code = client_msg.student_code
            log.content = content
            log.message = client_msg.context.message
            log.body = json.dumps(client_msg.context.body, ensure_ascii=False, separators=(',', ':'))
            log.device_id = client_msg.auth_license
            log.device = client_msg.device.dumps(with_license=True)
            log.msg_sign = client_msg.sign
            log.msg_timestamp = client_msg.timestamp
            log.msg_type = client_msg.context.context_type.value
            log.created_time = datetime.datetime.now()
            session.add(log)


if __name__ == '__main__':
    Log.metadata.drop_all(engine)
    Log.metadata.create_all(engine)
    a = ClientMessage(Device().from_core(), "31301188").send({"1234": 1232})
    Log.add(a)
