#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: taoting <taoting1234@gmail.com>

import datetime
import json

from sqlalchemy import Column, String, Integer, DateTime, and_

from models import Base, DBSession


class Heartbeat(Base):
    __tablename__ = 'heartbeat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_code = Column(String(100), nullable=False)
    course = Column(String(100), nullable=False)
    device = Column(String(100), nullable=False)
    create_time = Column(DateTime, nullable=False)


def add_heartbeat(student_code, course, device):
    session = DBSession()

    heartbeat = Heartbeat()
    heartbeat.student_code = student_code
    heartbeat.course = course
    heartbeat.device = json.dumps({
        'mac_addr': device.mac_addr,
        'hostname': device.hostname,
        'c_volume_serial_number': device.c_volume_serial_number
    })
    heartbeat.create_time = datetime.datetime.now()

    session.add(heartbeat)
    session.commit()


def get_people_number(course):
    session = DBSession()
    heartbeats = session.query(Heartbeat).filter(and_(
        Heartbeat.course == course,
        Heartbeat.create_time + 30 > datetime.datetime.now()
    )).all()
    res = set()
    for heartbeat in heartbeats:
        res.add(heartbeat.student_code)
    return len(res)


if __name__ == '__main__':
    pass
