#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>

import rsa

(public_key, private_key) = rsa.newkeys(1024)

# print(public_key.save_pkcs1())
a = public_key.save_pkcs1()
print(a)
print(a.split(b"\n"))
b = private_key.save_pkcs1()
print(b)
print(b.split(b"\n"))
