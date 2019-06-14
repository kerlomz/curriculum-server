#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>

import time
import logging
import datetime
import optparse
import threading
from concurrent import futures
from watchdog.observers import Observer

from models.heartbeat import Heartbeat
from models.log import Log
from models.user import User
from utils import *
from config import Config
from interface import InterfaceManager
from event_handler import FileEventHandler
from entity import ServerMessage, MessageType

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class TimeUtils(object):

    @staticmethod
    def datetime(compress=False):
        return datetime.datetime.now().strftime('%Y%m%d_%H_%M_%S.%f' if compress else '%Y-%m-%d %H:%M:%S.%f')


class BaseService(grpc_pb2_grpc.VerificationServicer):

    def __init__(self):
        self.response = ServerMessage()
        self.easy_response = lambda x: ResponseParser.dumps_response(self.response.send(x))
        self.standard_response = lambda x: ResponseParser.dumps_response(x)


class Verification(BaseService):

    @property
    def blacklist(self):
        with open("blacklist.txt", "r") as f:
            return f.readlines()

    def verification(self, request, context):
        """
        解析请求:
        plain_request.context.body: 消息主体; plain_request.device: 设备信息
        """
        plain_request = ResponseParser.parse(request=request.key)
        body = plain_request.context.body
        context_type = plain_request.context.context_type
        message = plain_request.context.message
        code = plain_request.context.code
        device = plain_request.device
        student_code = plain_request.student_code

        auth_logger.info("{} - [{}] | {} | {} | Device: [{}]".format(
            TimeUtils.datetime(), student_code, message, body, device
        ))

        if context_type == MessageType.Verify:  # 网络验证
            User.modify(plain_request, last_login_time=datetime.datetime.now(), last_online_time=datetime.datetime.now())
            Log.add(plain_request, "Login")
            return self.easy_response({"success": True if code >= 0 else False})
        elif context_type == MessageType.Heartbeat:  # 心跳
            User.modify(student_code, device.device_id, datetime.datetime.now())
            Heartbeat.add(plain_request, body['course'])
            return self.easy_response({"success": True if code >= 0 else False})
        elif context_type == MessageType.Logging:  # 日志
            Log.add(plain_request, "ClientLog")
            return self.easy_response({"success": True if code >= 0 else False})
        elif context_type == MessageType.Control:  # 控制频率
            delay_time = User.get_delay_time(student_code, body['course'])
            return self.easy_response({
                "message": {
                    'delay_time': delay_time
                },
                "success": True
            })

        return self.easy_response({})


class Predict(grpc_pb2_grpc.PredictServicer):

    def predict(self, request, context):
        start_time = time.time()
        bytes_batch, status = ImageUtils.get_bytes_batch(request.image)

        if interface_manager.total == 0:
            captcha_logger.info('There is currently no model deployment and services are not available.')
            return {"result": "", "success": False, "code": -999}

        if not bytes_batch:
            return grpc_pb2.PredictResult(result="", success=status['success'], code=status['code'])

        image_sample = bytes_batch[0]
        image_size = ImageUtils.size_of_image(image_sample)
        size_string = "{}x{}".format(image_size[0], image_size[1])
        if request.model_site:
            interface = interface_manager.get_by_sites(request.model_site, size_string,
                                                       strict=system_config.strict_sites)
        elif request.model_name:
            interface = interface_manager.get_by_name(request.model_name)
        elif request.model_type:
            interface = interface_manager.get_by_type_size(size_string, request.model_type)
        else:
            interface = interface_manager.get_by_size(size_string)
        if not interface:
            captcha_logger.info('Service is not ready!')
            return {"result": "", "success": False, "code": 999}

        image_batch, status = ImageUtils.get_image_batch(interface.model_conf, bytes_batch)

        if not image_batch:
            return grpc_pb2.PredictResult(result="", success=status['success'], code=status['code'])

        result = interface.predict_batch(image_batch, request.split_char)
        captcha_logger.info('[{}] [{}] - Size[{}] - Type[{}] - Site[{}] - Predict Result[{}] - {} ms'.format(
            TimeUtils.datetime(),
            interface.name,
            size_string,
            request.model_type,
            request.model_site,
            result,
            (time.time() - start_time) * 1000
        ))
        return grpc_pb2.PredictResult(result=result, success=status['success'], code=status['code'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb2_grpc.add_VerificationServicer_to_server(Verification(), server)
    grpc_pb2_grpc.add_PredictServicer_to_server(Predict(), server)
    server.add_insecure_port('[::]:{}'.format(server_port))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def event_loop():
    observer = Observer()
    event_handler = FileEventHandler(system_config, "model", interface_manager)
    observer.schedule(event_handler, event_handler.model_conf_path, True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', type="int", default=5449, dest="port")
    opt, args = parser.parse_args()
    server_port = opt.port

    server_host = "0.0.0.0"
    auth_logger = logging.getLogger(__name__ + "__auth__")
    auth_logger.setLevel(level=logging.INFO)
    auth_handler = logging.FileHandler("auth_log.txt")
    auth_stream_handler = logging.StreamHandler()
    auth_handler.setLevel(logging.INFO)
    auth_logger.addHandler(auth_handler)
    auth_logger.addHandler(auth_stream_handler)

    captcha_logger = logging.getLogger(__name__ + "__captcha__")
    captcha_logger.setLevel(level=logging.INFO)
    captcha_handler = logging.FileHandler("captcha_log.txt")
    captcha_stream_handler = logging.StreamHandler()
    captcha_handler.setLevel(logging.INFO)
    captcha_logger.addHandler(captcha_handler)
    captcha_logger.addHandler(captcha_stream_handler)

    system_config = Config(conf_path="./config.yaml", model_path="model", graph_path="graph")
    interface_manager = InterfaceManager()
    threading.Thread(target=event_loop).start()
    print('Running on http://{}:{}/ <Press CTRL + C to quit>'.format(server_host, server_port))
    serve()
