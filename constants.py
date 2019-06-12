#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>


class Response:

    def __init__(self):
        # SIGN
        self.INVALID_PUBLIC_PARAMS = dict(message='Invalid Public Params', code=400001, success=False)
        self.UNKNOWN_SERVER_ERROR = dict(message='Unknown Server Error', code=400002, success=False)
        self.INVALID_TIMESTAMP = dict(message='Invalid Timestamp', code=400004, success=False)
        self.INVALID_ACCESS_KEY = dict(message='Invalid Access Key', code=400005, success=False)
        self.INVALID_QUERY_STRING = dict(message='Invalid Query String', code=400006, success=False)

        # SERVER
        self.SUCCESS = dict(message=None, code=000000, success=True)
        self.INVALID_IMAGE_FORMAT = dict(message='Invalid Image Format', code=500001, success=False)
        self.INVALID_BASE64_STRING = dict(message='Invalid Base64 String', code=500002, success=False)
        self.IMAGE_DAMAGE = dict(message='Image Damage', code=500003, success=False)
        self.IMAGE_SIZE_NOT_MATCH_GRAPH = dict(message='Image Size Not Match Graph Value', code=500004, success=False)

    def find_message(self, _code):
        e = [value for value in vars(self).values()]
        _t = [i['message'] for i in e if i['code'] == _code]
        return _t[0] if _t else None

    def find(self, _code):
        e = [value for value in vars(self).values()]
        _t = [i for i in e if i['code'] == _code]
        return _t[0] if _t else None

    def all_code(self):
        return [i['message'] for i in [value for value in vars(self).values()]]


class Security:

    def __init__(self):

        self.__PUBLIC_KEY__ = [
            b'-----BEGIN RSA PUBLIC KEY-----',
            b'MIGJAoGBALSulIPX/S9BXP6v+3fFNfIKwkxuLJn28stzqqU+JW10IF3d+Azg05MO',
            b'gGKcuGVUXu0FrwfJNMEyg9oH1OWIod17WeDj06GAaCLm2ZRs7xa4TCYco2F1jLVx',
            b'/6/HR3MI1gBubp0OyykqAvE/TmAi15Hkt6NG8Bbtl4yY7Yl+iPnNAgMBAAE=',
            b'-----END RSA PUBLIC KEY-----',
            b''
        ]

        self.__PRIVATE_KEY__ = [
            b'-----BEGIN RSA PRIVATE KEY-----',
            b'MIICYAIBAAKBgQCSPP/UzNfjKGK4ipRLI+H+uV8YDbG3l3au7sHDfJAuUGyjvPR7',
            b'uaF3qhuhkFMyatfYnZl+cm8gbgS/1FlWauhA4yrQAiX7N+etnMz4G7Wcq93xZdv/',
            b'5M459TadnO0yBQ5bvsaJCvfmMP0LMhi5OYKw9eoXHHO7MkV1yfOauw7UyQIDAQAB',
            b'AoGAXihifMzL8FnvfmzT4LGg8JbAkMc4d0JRy361Sb4pQ3jLCn4+WG+EdH0Vv2gi',
            b'+WJryfBnhU//Fz1fV3hM7gi5pFgv10cLCE4wyY2tLwsgQnqieB1QbYHBcZRXxVTN',
            b'IUAt6EpV+Re1kJBFCYHwvbogKbeC5KrYiIbOFL6N4dbt/QECRQDMAxtH3wv45Xrh',
            b'yhNzNEtSJEb5fsKRyhfhgusIbFJbOesgzef6LiUlnWOtknX8zmlyqS0B7hL0oFie',
            b'jRGt7Bp7ir+yoQI9ALeA+CzjwOnGMP9/ET4VQuihMXZ03wmuY+QaZIEVLTfx82iA',
            b'lZyf/gc1qBADhMOLQnt+GyrK4MAU8vmZKQJEabsOb3Akd0kPJ2egLuuiQZ71faZ5',
            b'Vi9jswczofjpscfRmP29xQYXUGhCWZl3Np8PPVJ6Ne7ZuhhD9V/tErMzgmWFNiEC',
            b'PFaNvoFt69BYa0QX60odPTH81hfJiGpIl1VAHafFFU8OEIF6JRd7X5aG+H6VKkoR',
            b'pYoaMTY9+0SenPyeAQJFAI3Blvf1Ii5veeK+Wz451zSj9wSELb9T4JziM7GNCuB8',
            b'S1UJdWJHO6UoaxiHPjDqnBqxkXlGzkzIkIX7Nvxr7aU9KOX3',
            b'-----END RSA PRIVATE KEY-----',
            b''
        ]

    @property
    def public_key(self):
        return b"\n".join(self.__PUBLIC_KEY__)

    @property
    def private_key(self):
        return b"\n".join(self.__PRIVATE_KEY__)

