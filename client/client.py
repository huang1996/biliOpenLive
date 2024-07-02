# -*- coding: utf-8 -*-
# @Author: huang
# @Email: 676564115@qq.com
# @Date: 2024/6/4 19:52
# @File: client.py
# @Project: biliOpenLive
import urllib3
from requests import Session
from typing import Union, NamedTuple
import struct
import json
import hmac
import hashlib
import uuid
import datetime
import asyncio
import enum
import websocket
from websocket import WebSocketApp
from threading import Thread
from .models import *

urllib3.disable_warnings()

HEADER_STRUCT = struct.Struct('>I2H2I')


class HeaderTuple(NamedTuple):
    pack_len: int
    raw_header_size: int
    ver: int
    operation: int
    seq_id: int


class Operation(enum.IntEnum):
    """
    消息类型：
    OP_HEARTBEAT	2	客户端发送的心跳包(30秒发送一次)
    OP_HEARTBEAT_REPLY	3	服务器收到心跳包的回复
    OP_SEND_SMS_REPLY	5	服务器推送的弹幕消息包
    OP_AUTH	7	客户端发送的鉴权包(客户端发送的第一个包)
    OP_AUTH_REPLY	8	服务器收到鉴权包后的回复
    """
    OP_HEARTBEAT = 2
    OP_HEARTBEAT_REPLY = 3
    OP_SEND_SMS_REPLY = 5
    OP_AUTH = 7
    OP_AUTH_REPLY = 8


class Version(enum.IntEnum):
    """
    如果Version=0，Body中就是实际发送的数据。
    如果Version=2，Body中是经过压缩后的数据，请使用zlib解压，然后按照Proto协议去解析。
    """
    RAW_BODY = 0
    ZLIB_BODY = 2


class BaseMessageHandler:
    def __init__(self):
        pass

    def parser(self, message=None):
        header = HeaderTuple(*HEADER_STRUCT.unpack_from(message, 0))
        if header.operation == Operation.OP_HEARTBEAT_REPLY:
            # print(f'保活响应：{header}')
            pass
        elif header.operation == Operation.OP_SEND_SMS_REPLY:
            raw_data = json.loads(message[16:len(message)].decode('utf-8'))
            callback = self._call_function(raw_data)
            callback()

        elif header.operation == Operation.OP_AUTH_REPLY:
            data = message[16:len(message)].decode('utf-8')
            print(f'认证响应:{data}')
        else:
            print(f'未知响应:\r\n{header}')

    def _call_function(self, data: dict):
        if data['cmd'] in CMD_ACTIONS:
            method = getattr(self, CMD_ACTIONS[data['cmd']]['function'])
            def callback():
                msg = CMD_ACTIONS[data['cmd']]['model'](data['data'])
                method(msg)
            return callback
        else:
            print(f'未知消息类型：\r\n{data}')

    def on_message(self, app, message):
        self.parser(message)
        pass

    @staticmethod
    def on_danmu_message(message: DM):
        print(f'弹幕--{message.uname}[{message.fans_medal_name}{message.fans_medal_level}]:{message.msg}')

    @staticmethod
    def on_superchat_message(message: SuperChat):
        print(f'醒目留言--{message.uname}:{message.message}')

    @staticmethod
    def on_superchat_del(message: SuperChatDel):
        print(f'醒目留言清除--{message.room_id}:{message.message_ids}')

    @staticmethod
    def on_like_message(message: LikeMessage):
        print(f'点赞消息--{message.uname}:{message.open_id}')

    @staticmethod
    def on_interaction_end(message: InteractionEnd):
        print(f'消息推送结束--{message.game_id}:{message.timestamp}')

    @staticmethod
    def on_gift_message(message: GiftMessage):
        print(f'礼物--{message.uname}:{message.gift_name}')

    @staticmethod
    def on_guard_message(message: GuardMessage):
        print(f'上舰信息--{message.user_info}:{message.price}')


class BiliOpenLiveClient:
    def __init__(
            self,
            owner_code: str = None,
            access_key: str = None,
            access_secret_key: str = None,
            app_id: int = None,
            message_handler: BaseMessageHandler = None
    ):
        self.owner_code: str = owner_code
        self.access_key: str = access_key
        self.access_secret_key: str = access_secret_key
        self.app_id: int = app_id
        self.message_handler: BaseMessageHandler = message_handler
        self.main_url: str = f'https://live-open.biliapi.com'
        self.http_client: Session = Session()
        self.http_client.verify = False
        self.game_id = None
        self.wss_link = None
        self.auth_body = None
        self.ws_client = None

    def _make_signature(self, post_data: dict = None):
        self.http_client.headers.clear()

        self.http_client.headers = {
            'x-bili-accesskeyid': self.access_key,
            'x-bili-content-md5': hashlib.md5(json.dumps(post_data).encode('utf-8')).hexdigest(),
            'x-bili-signature-method': 'HMAC-SHA256',
            'x-bili-signature-nonce': uuid.uuid4().hex,
            'x-bili-signature-version': '1.0',
            'x-bili-timestamp': str(int(datetime.datetime.now().timestamp()))
        }

        str_to_sign = '\n'.join(
            f'{key}:{value}'
            for key, value in self.http_client.headers.items()
        )

        signature = hmac.new(
            self.access_secret_key.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256
        ).hexdigest()

        self.http_client.headers['Authorization'] = signature
        self.http_client.headers['Content-Type'] = 'application/json'
        self.http_client.headers['Accept'] = 'application/json'
        self.http_client.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                                                 '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

    def _base_http_request(self, path: str = None, body: dict = None) -> Union[dict, None]:
        if path is None or body is None:
            return None
        self._make_signature(body)
        url: str = f'{self.main_url}{path}'
        try:
            return self.http_client.post(url, data=json.dumps(body)).json()
        except Exception as e:
            print(f'在请求{url}时发生如下错误：\r\n{e}')

    @staticmethod
    def _make_pack(
            body: bytes = None,
            version: int = Version.RAW_BODY,
            operation: int = Operation.OP_HEARTBEAT) -> bytes:

        header = HeaderTuple(
            pack_len=(HEADER_STRUCT.size + (0 if body is None else len(body))),
            raw_header_size=HEADER_STRUCT.size,
            ver=version,
            operation=operation,
            seq_id=0
        )
        header_pack = HEADER_STRUCT.pack(*header)
        return header_pack

    def _base_ws_request(self, body: bytes = None, operation: int = Operation.OP_HEARTBEAT):
        pack = self._make_pack(body=body, operation=operation)

        if operation == Operation.OP_HEARTBEAT:
            self.ws_client.send(pack)
        else:
            self.ws_client.send(pack+body)

    def start_project(self) -> None:
        body = {
            "code": self.owner_code,
            "app_id": self.app_id
        }
        data = self._base_http_request(path='/v2/app/start', body=body)
        if data is None or data['code'] != 0:
            print(f'项目开启失败:\r\n{data}')
            return

        self.game_id = data['data']['game_info']['game_id']
        self.wss_link = data['data']['websocket_info']['wss_link']
        self.auth_body = data['data']['websocket_info']['auth_body']

        self.ws_client = websocket.create_connection(self.wss_link[0])
        self.ws_send_auth()
        Thread(target=self.ws_receive_message).start()
        asyncio.create_task(self._send_project_heart())
        asyncio.create_task(self.ws_send_heart())

    def end_project(self) -> None:
        body = {
            "app_id": self.app_id,
            "game_id": self.game_id
        }
        data = self._base_http_request(path='/v2/app/end', body=body)

    async def _send_project_heart(self, *, retry: int = 19) -> None:
        while True:
            await asyncio.sleep(retry)
            body = {
                "game_id": self.game_id
            }
            data = self._base_http_request(path='/v2/app/heartbeat', body=body)

    def ws_send_auth(self) -> None:
        self._base_ws_request(body=self.auth_body.encode('utf-8'), operation=Operation.OP_AUTH)

    async def ws_send_heart(self, retry=30) -> None:
        while True:
            await asyncio.sleep(retry)
            self._base_ws_request(operation=Operation.OP_HEARTBEAT)

    def ws_receive_message(self) -> None:
        while True:
            message = self.ws_client.recv()
            self.message_handler.parser(message=message)
