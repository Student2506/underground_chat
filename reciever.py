import asyncio
import datetime as dt
import sys
from contextlib import suppress

import aiofiles
import configargparse

if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def read_message(host: str, port: int, history: str):
    reader, _ = await asyncio.open_connection(host, port)

    while True:
        async with aiofiles.open(
            history, mode='a', encoding='utf-8'
        ) as f:
            data = await reader.readline()
            print(
                f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} '
                f'{data.decode().rstrip()}')
            await f.write(
                f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} '
                f'{data.decode()}'
            )
        await asyncio.sleep(0)


async def main(host: str, port: int, history: str):
    loop = asyncio.get_event_loop()
    read_func = loop.create_task(
        read_message(host=host, port=port, history=history)
    )
    while True:
        await read_func


if __name__ == '__main__':
    configs = configargparse.ArgParser(default_config_files=['.my_settings', ])
    configs.add(
        '-s', '--host', default='minechat.dvmn.org', help='host to connect'
    )
    configs.add(
        '-p', '--port', default=5000, help='port to use'
    )
    configs.add(
        '-l', '--history', default='chat.log', help='file to log'
    )
    configs.add(
        '-acc', '--ACCOUNT', default=None,
        help='Token is taken from .my_settings (not-used in server-side)'
    )
    options = configs.parse_args()
    with suppress(KeyboardInterrupt):
        asyncio.run(main(
            host=options.host,
            port=options.port,
            history=options.history))
