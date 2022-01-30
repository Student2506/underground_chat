import asyncio


async def main():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000
    )

    while True:
        data = await reader.readline()
        print(f'{data.decode().rstrip()}')


if __name__ == '__main__':
    asyncio.run(main())
