import asyncio
import aiofiles
import datetime as dt
import configargparse


async def read_message(options):
    reader, _ = await asyncio.open_connection(
        options.host, options.port
    )

    while True:
        async with aiofiles.open(options.history, mode='a') as f:
            data = await reader.readline()
            print(f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} {data.decode().rstrip()}')
            await f.write(f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} {data.decode()}')
        await asyncio.sleep(0)


async def main(options):
    loop = asyncio.get_event_loop()
    read_func = loop.create_task(read_message(options))
    
    while True:
        await read_func


if __name__ == '__main__':
    configs = configargparse.ArgParser(default_config_files=['.my_settings',])
    configs.add('-s', '--host', default='minechat.dvmn.org', help='host to connect')
    configs.add('-p', '--port', default=5000, help='port to use')
    configs.add('-l', '--history', default='chat.log', help='file to log')
    options = configs.parse_args()
    try:
        asyncio.run(main(options))
    except KeyboardInterrupt:
        pass
