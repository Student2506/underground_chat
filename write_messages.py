import asyncio
import configargparse


ACCOUNT = '6c791ca6-81c4-11ec-8c47-0242ac110002'


async def write_message(options):
    reader, writer = await asyncio.open_connection(
        options.host, 5050
    )
    await asyncio.sleep(5)
    data = await reader.readline()
    print(data)
    writer.write((ACCOUNT + '\n').encode())
    data = await reader.readline()
    print(data.decode())
    await asyncio.sleep(5)
    message = 'Я снова тестирую чатик. Это третье сообщение.\n\n'
    writer.write(message.encode())
    writer.close()


async def main(options):
    loop = asyncio.get_event_loop()
    write_func = loop.create_task(write_message(options))
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
    options = configs.parse_args()
    try:
        asyncio.run(main(options))
    except KeyboardInterrupt:
        pass

