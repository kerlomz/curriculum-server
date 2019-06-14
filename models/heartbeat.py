#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime

from sqlalchemy import Column, String, Integer, DateTime, and_

from models import Base, engine, session_maker
from models.log import Log
from entity import Device, ClientMessage
from core import Core


class Heartbeat(Base):
    __tablename__ = 'heartbeat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    course = Column(String(100), nullable=False)
    device = Column(String(256), nullable=False)
    device_id = Column(String(128), nullable=False)
    created_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Heartbeat(id='%s', student_code='%s', course='%s', device='%s', device_id='%s', created_time='%s')>" % (
            self.id,
            self.student_code,
            self.course,
            self.device,
            self.device_id,
            self.created_time
        )

    @classmethod
    def add(cls, client_msg: ClientMessage, course: str):
        with session_maker() as session:
            heartbeat = cls()
            heartbeat.student_code = client_msg.student_code
            heartbeat.course = course
            heartbeat.device = client_msg.device.dumps()
            heartbeat.device_id = client_msg.auth_license
            calc_device_id = Core.machine_code_auth(
                stu_code=client_msg.student_code,
                mac_addr=client_msg.device.mac_addr,
                c_volume_serial_number=client_msg.device.c_volume_serial_number,
                hostname=client_msg.device.hostname
            )
            if calc_device_id != client_msg.auth_license:
                Log.add(client_msg)
            heartbeat.created_time = datetime.datetime.now()
            session.add(heartbeat)

    @classmethod
    def get_people_number(cls, course):
        with session_maker() as session:
            heartbeats = session.query(cls).filter(and_(
                cls.course == course,
                cls.created_time + 30 > datetime.datetime.now()
            )).all()
            res = set()
            for heartbeat in heartbeats:
                res.add(heartbeat.student_code)
            return len(res)


if __name__ == '__main__':
    Heartbeat.metadata.drop_all(engine)
    Heartbeat.metadata.create_all(engine)
    a = Device().from_core()
    t = a.auth_license.update({"31301188": 'fdsfa'})
    c = ClientMessage(device=a, stu_code="31301188")
    Heartbeat.add(c.send({}), "aaa")
    # print(h)

    # Log.add(
    #     student_code="",
    #     message="iopiop",
    #     body={"123": 123},
    #     device_id="89789789",
    #     mac_addr="hjkhjkhjkhjk"
    # )
    r = Heartbeat.get_people_number("aaa")
    print(r)
