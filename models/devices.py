#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import json
import datetime

from sqlalchemy import Column, String, Integer, DateTime, and_

from models import Base, engine, session_maker
from models.log import Log
from entity import Device, ClientMessage
from core import Core


class Devices(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mac_addr = Column(String(64), nullable=True)
    hostname = Column(String(128), nullable=True)
    c_volume_serial_number = Column(String(256), nullable=True)
    device_id = Column(String(128), nullable=False, unique=True)
    student_codes = Column(String(512), nullable=True)
    created_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return "<Device(id='%s', mac_addr='%s', hostname='%s', c_volume_serial_number='%s', device_id='%s', student_codes='%s', created_time='%s')>" % (
            self.id,
            self.mac_addr,
            self.hostname,
            self.c_volume_serial_number,
            self.device_id,
            self.student_codes,
            self.created_time
        )

    @classmethod
    def add(cls, client_msg: ClientMessage):
        with session_maker() as session:
            device = cls()

            stu_codes = session.query(Devices.student_codes).filter(Devices.device_id == client_msg.device.device_id).first()

            if stu_codes:
                stu_codes = json.loads(stu_codes[0]) if stu_codes else []
                stu_codes = list(set([client_msg.student_code] + stu_codes))
                stu_codes = json.dumps(stu_codes, ensure_ascii=False, separators=(',', ':'))
                session.query(Devices).filter(Devices.device_id == client_msg.device.device_id).update(
                    {Devices.student_codes: stu_codes}
                )
            else:
                stu_codes = json.dumps([client_msg.student_code], ensure_ascii=False, separators=(',', ':'))
                device.student_codes = stu_codes
                device.hostname = client_msg.device.hostname
                device.mac_addr = client_msg.device.mac_addr
                device.c_volume_serial_number = client_msg.device.c_volume_serial_number
                device.device_id = client_msg.device.device_id
                device.created_time = datetime.datetime.now()
                session.add(device)

            calc_auth_license = Core.machine_code_auth(
                stu_code=client_msg.student_code,
                mac_addr=client_msg.device.mac_addr,
                c_volume_serial_number=client_msg.device.c_volume_serial_number,
                hostname=client_msg.device.hostname
            )
            if calc_auth_license != client_msg.auth_license:
                Log.add(client_msg)


if __name__ == '__main__':
    # Devices.metadata.drop_all(engine)
    # Devices.metadata.create_all(engine)
    Devices().add(ClientMessage(Device().from_core(), stu_code="31301187").send({}))

