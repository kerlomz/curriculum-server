#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import time
import hashlib
import base64
import socket
from psutil import net_if_addrs
from utils import RSAUtils
from entity import Device


class Core:

    @staticmethod
    def machine_code_auth(stu_code, c_volume_serial_number, mac_addr, hostname):
        auth_code = base64.b64encode(
            hashlib.md5("\u0000\u9999\0||{}||{}||{}||{}||\n\r\0\u8888".format(
                stu_code, c_volume_serial_number, mac_addr, hostname
            ).encode('utf8')).hexdigest().encode("utf8")
        ).decode()
        return auth_code[:6] + auth_code[-10:]

    @property
    def mac_addr(self):
        return [v[0][1] for v in net_if_addrs().values() if len(v[0][1]) == 17][0]

    @property
    def hostname(self):
        return socket.gethostname()

    @property
    def c_volume_serial_number(self):
        try:
            import win32api
            c_volume_serial_number = win32api.GetVolumeInformation("C:\\")[1]
            return str(c_volume_serial_number)
        except ImportError:
            return 0

    @classmethod
    def machine_code(cls, stu_code):
        c_volume_serial_number = cls.c_volume_serial_number
        mac = [v[0][1] for v in net_if_addrs().values() if len(v[0][1]) == 17][0]
        hostname = socket.gethostname()
        plain_text = "{}||{}||{}||{}||{}".format(stu_code, c_volume_serial_number, mac, hostname, time.time())
        encrypted = RSAUtils.encrypt(plain_text)
        encrypted = encrypted.replace("1", ")").replace("9", "{").replace("E", "&").replace("b", "%")
        encrypted = encrypted.replace(")", "9").replace("{", "1")
        return encrypted

    @classmethod
    def decrypt_auth(cls, key):
        key = key.replace("9", ")").replace("1", "{")
        key = key.replace(")", "1").replace("{", "9").replace("&", "E").replace("%", "b")
        plain_text = RSAUtils.decrypt(key)
        device_group = plain_text.split("||")
        stu_code = device_group[0]
        c_volume_serial_number = device_group[1]
        mac = device_group[2]
        hostname = device_group[3]
        auth_code = cls.machine_code_auth(stu_code, c_volume_serial_number, mac, hostname)
        return auth_code

    @classmethod
    def decrypt_auth2object(cls, machine_code) -> Device:
        key = machine_code.replace("9", ")").replace("1", "{")
        key = key.replace(")", "1").replace("{", "9").replace("&", "E").replace("%", "b")
        plain_text = RSAUtils.decrypt(key)
        device_group = plain_text.split("||")
        stu_code = device_group[0]
        c_volume_serial_number = device_group[1]
        mac_addr = device_group[2]
        hostname = device_group[3]
        device = Device(mac_addr=mac_addr, hostname=hostname, c_volume_serial_number=c_volume_serial_number)
        machine_code_auth = cls.machine_code_auth(stu_code, c_volume_serial_number, mac_addr, hostname)
        device.add_license(stu_code, machine_code_auth)
        return device


if __name__ == '__main__':
    r = Core.decrypt_auth(
        "O/zxgDfnn3+4&5/y5sK3t%aah4C6nM2zx9x40/JcM%tzUW50H0PpdQ%4W3/kA9N/VneyLs8rSD719s2e1/p4C/epVXdWONnK0lR4gPaHFVJka5qzDynfuwGdtAcP0S&Xi7hyuHjcDh0zi58Ui1CuUIZvq4dkLnsMwCrrS2zRzXQ=")
    print(r)
