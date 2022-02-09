import asyncio
import json
import logging
import re
import sys
import tkinter as tk
from anyio import run, create_task_group
from contextlib import suppress

import aiofiles
import configargparse

from gui import update_tk

if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

log = logging.getLogger(__name__)


async def register_user(host: str, port: int, queue):
    username = await queue.get()
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
    raise KeyboardInterrupt


class User_Creation:
    def __init__(self, master, host, port, queue):
        self.host = host
        self.port = port
        self.queue = queue
        self.username = tk.Entry(master, width=20)
        self.create_token = tk.Button(master, text='create token', width=20)
        self.label = tk.Label(master, width=20, bg='black', fg='white')
        self.create_token['command'] = getattr(self, 'creation')
        self.username.pack()
        self.create_token.pack()

    def creation(self):
        username = self.username.get()
        self.queue.put_nowait(username)
        self.username.delete(0, tk.END)
        # register_user(self.host, self.port, username)


async def main():
    FORMAT = '%(levelname)s:%(funcName)s:%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    configs = configargparse.ArgParser()
    configs.add(
        '-s', '--host', default='minechat.dvmn.org', help='host to connect'
    )
    configs.add(
        '-p', '--port', default=5050, help='port to use'
    )
    options = configs.parse_args()
    queue = asyncio.Queue()

    root = tk.Tk()
    root.title('Создание пользователя')

    root_frame = tk.Frame()
    root_frame.pack(fill='both', expand=True)

    User_Creation(
        root_frame, options.host, options.port, queue
    )
    try:
        async with create_task_group() as tg:
            tg.start_soon(update_tk, root_frame)
            tg.start_soon(register_user, options.host, options.port, queue)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        run(main)
