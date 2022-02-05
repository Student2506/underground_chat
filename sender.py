import asyncio
import json
import logging
import re
import sys
from contextlib import suppress

import aiofiles
import configargparse

if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

FORMAT = '%(levelname)s:%(funcName)s:%(message)s'


logging.basicConfig(level=logging.DEBUG, format=FORMAT)
log = logging.getLogger(__name__)


async def register_user(host: str, port: int, username: str):
    username = re.sub('[^A-Za-z0-9]+', '', username)
    reader, writer = await asyncio.open_connection(host, port)
    await asyncio.sleep(1)
    data = await reader.readline()
    log.debug(data.decode())
    writer.write('\n'.encode())
    await writer.drain()
    data = await reader.readline()
    log.debug(data.decode())
    writer.write((username + '\n\n').encode())
    await writer.drain()
    data = await reader.readline()
    data = json.loads(data.decode())
    log.debug(data)
    async with aiofiles.open('.my_settings', mode='wb') as f:
        log.debug(f'ACCOUNT={data.get("account_hash")}\n'.encode())
        await f.write(f'ACCOUNT={data.get("account_hash")}\n'.encode())


async def authorize(account, reader, writer):
    data = await reader.readline()
    log.debug(data.decode())
    writer.write((account + '\n').encode())
    await writer.drain()
    data = await reader.readline()
    if json.loads(data.decode()) is None:
        log.debug(
            'Неизвестный токен. Проверьте его или зарегистрируйте заново.\n'
        )
        return False
    log.debug(data.decode())
    return True


async def submit_message(host, port, account, message):
    reader, writer = await asyncio.open_connection(host, port)
    await asyncio.sleep(5)
    if not await authorize(account, reader, writer):
        return
    await asyncio.sleep(5)
    message_to_send = re.sub('[^A-Za-zА-Яа-я0-9 ]+', '', message)
    log.debug(message_to_send)
    writer.write((message_to_send+'\n\n').encode())
    await writer.drain()
    writer.close()


async def main(
    host: str,
    port: int,
    account: str,
    username: str,
    message: str
):
    loop = asyncio.get_event_loop()
    if username:
        register = loop.create_task(
            register_user(host, port, username)
        )
        await register
        return
    if not account:
        log.debug('Требуется запуск с ключём --username')
        return
    write_func = loop.create_task(
        submit_message(host, port, account, message)
    )
    await write_func


if __name__ == '__main__':
    configs = configargparse.ArgParser(default_config_files=['.my_settings', ])
    configs.add(
        '-s', '--host', default='minechat.dvmn.org', help='host to connect'
    )
    configs.add(
        '-p', '--port', default=5050, help='port to use'
    )
    configs.add(
        '-acc', '--ACCOUNT', default=None,
        help='Token is taken from .my_settings'
    )
    configs.add(
        '-user', '--username', default=None, help='Username to use'
    )
    configs.add(
        '-m', '--message', required=True, help='Text to send'
    )
    options = configs.parse_args()

    with suppress(KeyboardInterrupt):
        asyncio.run(main(
            options.host, options.port, options.ACCOUNT,
            options.username, options.message
        ))
