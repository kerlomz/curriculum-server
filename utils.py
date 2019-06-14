#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kerlomz <kerlomz@gmail.com>
import io
import cv2
import grpc
import base64
import pickle
import binascii
import grpc_pb2
import grpc_pb2_grpc
import numpy as np
from PIL import Image as PIL_Image
from pretreatment import preprocessing
from config import ModelConfig
from constants import Response
from entity import ClientMessage
from core import RSAUtils


class Cache(object):

    @staticmethod
    def save(obj):
        return pickle.dumps(obj) if obj else obj

    @staticmethod
    def open(obj):
        return pickle.loads(obj) if obj else obj


class PathUtils(object):

    @staticmethod
    def get_file_name(path: str):
        if '/' in path:
            return path.split('/')[-1]
        elif '\\' in path:
            return path.split('\\')[-1]
        else:
            return path


class ImageUtils(object):

    def __init__(self, model: ModelConfig):
        self.model = model

    @staticmethod
    def get_bytes_batch(base64_or_bytes):
        response = Response()
        try:
            if isinstance(base64_or_bytes, bytes):
                bytes_batch = [base64_or_bytes]
            elif isinstance(base64_or_bytes, list):
                bytes_batch = [base64.b64decode(i.encode('utf-8')) for i in base64_or_bytes if isinstance(i, str)]
                if not bytes_batch:
                    bytes_batch = [base64.b64decode(i) for i in base64_or_bytes if isinstance(i, bytes)]
            else:
                bytes_batch = base64.b64decode(base64_or_bytes.encode('utf-8')).split(b'\x00\xff\xff\xff\x00')
        except binascii.Error:
            return None, response.INVALID_BASE64_STRING
        what_img = [ImageUtils.test_image(i) for i in bytes_batch]
        if None in what_img:
            return None, response.INVALID_IMAGE_FORMAT
        return bytes_batch, response.SUCCESS

    @staticmethod
    def get_image_batch(model: ModelConfig, bytes_batch):
        # Note that there are two return objects here.
        # 1.image_batch, 2.response

        response = Response()

        def load_image(image_bytes):
            data_stream = io.BytesIO(image_bytes)
            pil_image = PIL_Image.open(data_stream)
            rgb = pil_image.split()
            size = pil_image.size

            if len(rgb) > 3 and model.replace_transparent:
                background = PIL_Image.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, (0, 0, size[0], size[1]), pil_image)
                pil_image = background

            if model.image_channel == 1:
                pil_image = pil_image.convert('L')

            # image = cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2GRAY)
            image = preprocessing(np.asarray(pil_image), model.binaryzation, model.smooth, model.blur).astype(
                np.float32)
            if model.resize[0] == -1:
                ratio = model.resize[1] / size[1]
                resize_width = int(ratio * size[0])
                print(resize_width, model.resize[1])
                image = cv2.resize(image, (resize_width, model.resize[1]))
            else:
                image = cv2.resize(image, (model.resize[0], model.resize[1]))
            image = image.swapaxes(0, 1)
            return (image[:, :, np.newaxis] if model.image_channel == 1 else image[:, :]) / 255.

        try:
            image_batch = [load_image(i) for i in bytes_batch]
            return image_batch, response.SUCCESS
        except OSError:
            return None, response.IMAGE_DAMAGE
        except ValueError as _e:
            print(_e)
            return None, response.IMAGE_SIZE_NOT_MATCH_GRAPH

    @staticmethod
    def pil_image(image_bytes):
        data_stream = io.BytesIO(image_bytes)
        pil_image = PIL_Image.open(data_stream).convert('RGB')
        return pil_image

    @staticmethod
    def size_of_image(image_bytes: bytes):
        _null_size = tuple((-1, -1))
        try:
            data_stream = io.BytesIO(image_bytes)
            size = PIL_Image.open(data_stream).size
            return size
        except OSError:
            return _null_size
        except ValueError:
            return _null_size

    @staticmethod
    def test_image(h):
        """JPEG"""
        if h[:3] == b"\xff\xd8\xff":
            return 'jpeg'
        """PNG"""
        if h[:8] == b"\211PNG\r\n\032\n":
            return 'png'
        """GIF ('87 and '89 variants)"""
        if h[:6] in (b'GIF87a', b'GIF89a'):
            return 'gif'
        """TIFF (can be in Motorola or Intel byte order)"""
        if h[:2] in (b'MM', b'II'):
            return 'tiff'
        if h[:2] == b'BM':
            return 'bmp'
        """SGI image library"""
        if h[:2] == b'\001\332':
            return 'rgb'
        """PBM (portable bitmap)"""
        if len(h) >= 3 and \
                h[0] == b'P' and h[1] in b'14' and h[2] in b' \t\n\r':
            return 'pbm'
        """PGM (portable graymap)"""
        if len(h) >= 3 and \
                h[0] == b'P' and h[1] in b'25' and h[2] in b' \t\n\r':
            return 'pgm'
        """PPM (portable pixmap)"""
        if len(h) >= 3 and h[0] == b'P' and h[1] in b'36' and h[2] in b' \t\n\r':
            return 'ppm'
        """Sun raster file"""
        if h[:4] == b'\x59\xA6\x6A\x95':
            return 'rast'
        """X bitmap (X10 or X11)"""
        s = b'#define '
        if h[:len(s)] == s:
            return 'xbm'
        return None


class ResponseParser(object):

    def __init__(self, host: str, port):
        self._url = '{}:{}'.format(host, port)

    def request(self, key, encrypted=True) -> ClientMessage:
        channel = grpc.insecure_channel(self._url)
        stub = grpc_pb2_grpc.VerificationStub(channel)
        response = stub.verification(grpc_pb2.VerificationRequest(
            key=self.dumps(key) if encrypted else key
        ))
        return self.parse(response.result)

    @staticmethod
    def dumps_response(key) -> grpc_pb2.VerificationResult:
        return grpc_pb2.VerificationResult(result=ResponseParser.dumps(key))

    @staticmethod
    def parse(request) -> ClientMessage:
        decrypted_object = RSAUtils.decrypt(request, decode=False)
        return Cache.open(decrypted_object)

    @staticmethod
    def dumps(response):
        return RSAUtils.encrypt(Cache.save(response))
