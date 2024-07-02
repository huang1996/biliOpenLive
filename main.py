from client.client import *
import asyncio


# 在开放平台申请的开发者密钥
ACCESS_KEY_ID = ''
ACCESS_KEY_SECRET = ''
# 在开放平台创建的项目ID
APP_ID = 0000
# 主播身份码
ROOM_OWNER_AUTH_CODE = ''


async def main():
    client = BiliOpenLiveClient(
        owner_code=ROOM_OWNER_AUTH_CODE,
        access_key=ACCESS_KEY_ID,
        access_secret_key=ACCESS_KEY_SECRET,
        app_id=APP_ID,
        message_handler=BaseMessageHandler()
    )
    client.start_project()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
