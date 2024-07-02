# -*- coding: utf-8 -*-
# @Author: huang
# @Email: 676564115@qq.com
# @Date: 2024/6/5 11:03
# @File: models.py
# @Project: biliOpenLive
import enum
import json


class Base:
    def __init__(self, data: dict):
        for key in data:
            has_filed = hasattr(self, key)
            # filed = getattr(self, key)
            if has_filed:
                super().__setattr__(key, data[key])

    def json(self):
        return json.dumps(self.__dict__)


class DM(Base):
    """
    uname\tstring\t用户昵称\r\n
    uid\tint64\t用户UID（已废弃，固定为0）\r\n
    open_id\tstring\t用户唯一标识\r\n
    uface\tstring\t用户头像\r\n
    timestamp\tint64\t弹幕发送时间秒级时间戳\r\n
    room_id\tint64\t弹幕接收的直播间\r\n
    msg\tstring\t弹幕内容\r\n
    msg_id\tstring\t消息唯一id\r\n
    guard_level\tint64\t对应房间大航海等级\r\n
    fans_medal_wearing_status\tbool\t该房间粉丝勋章佩戴情况\r\n
    fans_medal_name\tstring\t粉丝勋章名\r\n
    fans_medal_level\tint64\t对应房间勋章信息\r\n
    emoji_img_url\tstring\t表情包图片地址\r\n
    dm_type\tint64\t弹幕类型\t0：普通弹幕\t1：表情包弹幕\r\n
    """

    uname: str = None
    uid: int = None
    open_id: str = None
    uface: str = None
    timestamp: int = None
    room_id: int = None
    msg: str = None
    msg_id: str = None
    guard_level: int = None
    fans_medal_wearing_status: bool = None
    fans_medal_name: str = None
    fans_medal_level: int = None
    emoji_img_url: str = None
    dm_type: int = None

    def __init__(self, body: dict):
        super(DM, self).__init__(body)


class SuperChat(Base):
    room_id: int = None
    uid: int = None
    open_id: str = None
    uname: str = None
    uface: str = None
    message_id: int = None
    message: str = None
    rmb: int = None
    timestamp: int = None
    start_time: int = None
    end_time: int = None
    guard_level: int = None
    fans_medal_level: int = None
    fans_medal_name: str = None
    fans_medal_wearing_status: bool = None
    msg_id: str = None

    def __init__(self, body: dict):
        super(SuperChat, self).__init__(body)


class SuperChatDel(Base):
    room_id: int = None
    message_ids: list
    int = None
    msg_id: str = None

    def __init__(self, body: dict):
        super(SuperChatDel, self).__init__(body)


class LikeMessage(Base):
    uname: str = None
    uid: int = None
    open_id: str = None
    uface: str = None
    timestamp: int = None
    room_id: int = None
    like_text: str = None
    like_count: int = None
    fans_medal_wearing_status: bool = None
    fans_medal_name: str = None
    fans_medal_level: int = None

    def __init__(self, body: dict):
        super(LikeMessage, self).__init__(body)


class InteractionEnd(Base):
    game_id: str = None
    timestamp: int = None

    def __init__(self, body: dict):
        super(InteractionEnd, self).__init__(body)


class AnchorInfo(Base):
    uid: int = None
    open_id: str = None
    uname: str = None
    uface: str = None

    def __init__(self, body: dict):
        super(AnchorInfo, self).__init__(body)


class ComboInfo(Base):
    combo_base_num: int = None
    combo_count: int = None
    combo_id: str = None
    combo_timeout: int = None

    def __init__(self, body: dict):
        super(ComboInfo, self).__init__(body)


class GiftMessage(Base):
    room_id: int = None
    uid: int = None
    open_id: str = None
    uname: str = None
    uface: str = None
    gift_id: int = None
    gift_name: str = None
    gift_num: int = None
    price: int = None
    paid: bool = None
    fans_medal_level: int = None
    fans_medal_name: str = None
    fans_medal_wearing_status: bool = None
    guard_level: int = None
    timestamp: int = None
    anchor_info: AnchorInfo = None
    msg_id: str = None
    gift_icon: str = None
    combo_gift: bool = None
    combo_info: ComboInfo = None

    def __init__(self, body: dict):
        super(GiftMessage, self).__init__(body)


class UserInfo(Base):
    uid: int = None
    open_id: str = None
    uname: str = None
    uface: str = None

    def __init__(self, body: dict):
        super(UserInfo, self).__init__(body)


class GuardMessage(Base):
    user_info: UserInfo = None
    guard_level: int = None
    guard_num: int = None
    guard_unit: str = None
    price: int = None
    fans_medal_level: int = None
    fans_medal_name: str = None
    fans_medal_wearing_status: bool = None
    room_id: int = None
    msg_id: str = None
    timestamp: int = None

    def __init__(self, body: dict):
        super(GuardMessage, self).__init__(body)


CMD_ACTIONS = dict({
    'LIVE_OPEN_PLATFORM_DM': {
        'function': 'on_danmu_message',
        'model': DM
    },
    'LIVE_OPEN_PLATFORM_SUPER_CHAT': {
        'function': 'on_superchat_message',
        'model': SuperChat
    },
    'LIVE_OPEN_PLATFORM_SUPER_CHAT_DEL': {
        'function': 'on_superchat_del',
        'model': SuperChatDel
    },
    'LIVE_OPEN_PLATFORM_LIKE': {
        'function': 'on_like_message',
        'model': LikeMessage
    }, 'LIVE_OPEN_PLATFORM_INTERACTION_END': {
        'function': 'on_interaction_end',
        'model': InteractionEnd
    }, 'LIVE_OPEN_PLATFORM_SEND_GIFT': {
        'function': 'on_gift_message',
        'model': GiftMessage
    }, 'LIVE_OPEN_PLATFORM_GUARD': {
        'function': 'on_guard_message',
        'model': GuardMessage
    }
})
