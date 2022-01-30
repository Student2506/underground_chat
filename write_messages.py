import asyncio
import json
import logging

import aiofiles
import configargparse

# FORMAT_OLD = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
FORMAT = '%(levelname)s:%(funcName)s:%(message)s'


logging.basicConfig(level=logging.DEBUG, format=FORMAT)
log = logging.getLogger(__name__)


async def register_user(options):
    reader, writer = await asyncio.open_connection(
        options.host, options.port
    )
    await asyncio.sleep(1)
    data = await reader.readline()
    log.debug(data.decode())
    writer.write('\n'.encode())
    data = await reader.readline()
    log.debug(data.decode())
    writer.write((options.username + '\n\n').encode())
    data = await reader.readline()
    data = json.loads(data.decode())
    log.debug(data)
    async with aiofiles.open('.my_settings', mode='wb') as f:
        log.debug(f'ACCOUNT={data.get("account_hash")}\n'.encode())
        await f.write(f'ACCOUNT={data.get("account_hash")}\n'.encode())


async def authorize(options, reader, writer):
    data = await reader.readline()
    log.debug(data.decode())
    writer.write((options.ACCOUNT + '\n').encode())
    data = await reader.readline()
    if json.loads(data.decode()) is None:
        log.debug(
            'Неизвестный токен. Проверьте его или зарегистрируйте заново.\n'
        )
        return False
    log.debug(data.decode())
    return True


async def submit_message(options):
    reader, writer = await asyncio.open_connection(
        options.host, options.port
    )
    await asyncio.sleep(5)
    if not await authorize(options, reader, writer):
        return
    await asyncio.sleep(5)
    message = 'Я снова тестирую чатик. Это третье сообщение.\n\n'
    writer.write(message.encode())
    writer.close()


async def main(options):
    loop = asyncio.get_event_loop()
    if options.username is not None:
        register = loop.create_task(register_user(options))
        await register
        return
    if options.ACCOUNT is None:
        log.debug('Register yourself')
        return
    write_func = loop.create_task(submit_message(options))
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
        '-l', '--history', default='chat.log', help='file to log'
    )
    configs.add(
        '-acc', '--ACCOUNT', default=None, help='Account to use'
    )
    configs.add(
        '-user', '--username', default=None, help='Username to use'
    )
    options = configs.parse_args()
    try:
        asyncio.run(main(options))
    except KeyboardInterrupt:
        pass
