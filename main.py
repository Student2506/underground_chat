import asyncio


async def read_message():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000
    )

    while True:
        data = await reader.readline()
        print(f'{data.decode().rstrip()}')
        await asyncio.sleep(0)


async def main():
    loop = asyncio.get_event_loop()
    read_func = loop.create_task(read_message())
    
    while True:
        await read_func


if __name__ == '__main__':
    asyncio.run(main())
