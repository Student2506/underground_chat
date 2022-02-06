import asyncio
import datetime as dt
import json
import logging
import re
import sys
import time
from contextlib import suppress
from tkinter import TclError, messagebox

import aiofiles
import configargparse
from anyio import create_task_group, run
from async_timeout import timeout

import gui

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

watchdog_logger = logging.getLogger(__name__)

if (sys.version_info[0] == 3 and sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class InvalidToken(Exception):
    pass


async def save_messages(filepath: str, queue: asyncio.Queue):
    while True:
        async with aiofiles.open(
            filepath, mode='a', encoding='utf-8'
        ) as f:
            msg = await queue.get()
            await f.write(msg + '\n')


async def read_msgs(
    host: str,
    port: int,
    queue: asyncio.Queue,
    logging_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue
):
    status_queue.put_nowait(gui.ReadConnectionStateChanged.INITIATED)
    try:
        reader, _ = await asyncio.open_connection(host, port)
    except TimeoutError:
        status_queue.put_nowait(gui.ReadConnectionStateChanged.CLOSED)
        return
    status_queue.put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)
    while True:
        data = await reader.readline()
        watchdog_queue.put_nowait(
            f'[{int(time.time())}] '
            'Connection is alive. New message in chat.'
        )
        logging_queue.put_nowait(
            f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} '
            f'{data.decode().rstrip()}'
        )
        queue.put_nowait(
            f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} '
            f'{data.decode().rstrip()}')


async def send_msgs(
    host: str,
    port: int,
    queue: asyncio.Queue,
    account: str,
    logging_queue: asyncio.Queue,
    status_queue: asyncio.Queue,
    watchdog_queue: asyncio.Queue
):
    status_queue.put_nowait(gui.SendingConnectionStateChanged.INITIATED)
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except TimeoutError:
        status_queue.put_nowait(gui.SendingConnectionStateChanged.CLOSED)
        return
    try:
        data = await reader.readline()
        watchdog_queue.put_nowait(
            f'[{int(time.time())}] Connections is alive. Message sent.'
        )
        logging_queue.put_nowait(data.decode())
        writer.write((account + '\n').encode())
        await writer.drain()
        data = await reader.readline()
        watchdog_queue.put_nowait(
            f'[{int(time.time())}] Connections is alive. Prompt before auth.'
        )
        if json.loads(data.decode()) is None:
            raise InvalidToken
        nickname = json.loads(data.decode()).get('nickname')
        event = gui.NicknameReceived(nickname)
        status_queue.put_nowait(event)
        logging_queue.put_nowait(
            f'Выполнена авторизация. Пользователь {nickname}'
        )
        watchdog_queue.put_nowait(
            f'[{int(time.time())}] Connections is alive. Authorization done.'
        )
        status_queue.put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)
    except (ConnectionResetError, TimeoutError):
        logging_queue.put_nowait('Соединение не установлено')
        return
    while True:
        msg = await queue.get()
        message_to_send = re.sub('[^A-Za-zА-Яа-я0-9 ]+', '', msg)
        writer.write((message_to_send+'\n\n').encode())
        await writer.drain()
        watchdog_queue.put_nowait(
            f'[{int(time.time())}] Connections is alive. Message sent.'
        )


async def watch_for_connection(watchdog_queue: asyncio.Queue):
    while True:
        try:
            async with timeout(1.0) as cm:
                message = await watchdog_queue.get()
                print(message)
        except asyncio.TimeoutError:
            if cm.expired:
                print(f'[{int(time.time())}] 1s timeout is elapsed.')


async def handle_connection():
    pass


async def main():
    configs = configargparse.ArgParser(default_config_files=['.my_settings', ])
    configs.add(
        '-s', '--host', default='minechat.dvmn.org', help='host to connect'
    )
    configs.add(
        '-p', '--port', default=5000, help='port to recieve messages'
    )
    configs.add(
        '-acc', '--ACCOUNT', default=None,
        help='Token is taken from .my_settings'
    )
    configs.add(
        '-l', '--history', default='chat.log', help='file to log'
    )
    configs.add(
        '-user', '--username', default=None, help='Username to use'
    )
    configs.add(
        '-send', '--secondary_port', default=5050, help='port to send messages'
    )
    options = configs.parse_args()
    print(options)
    exit()

    host = options.host
    port = options.port
    history_filename = options.history
    account = options.ACCOUNT
    send_port = options.secondary_port

    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    logging_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()
    async with aiofiles.open(
        history_filename, mode='r', encoding='utf-8'
    ) as f:
        history = await f.readlines()
    for line in history:
        messages_queue.put_nowait(line.rstrip())
    try:
        async with create_task_group() as tg:
            tg.start_soon(
                gui.draw, messages_queue, sending_queue, status_updates_queue
            )
            tg.start_soon(
                read_msgs, host, port, messages_queue, logging_queue,
                status_updates_queue, watchdog_queue
            )
            tg.start_soon(save_messages, history_filename, logging_queue)
            tg.start_soon(
                send_msgs, host, send_port, sending_queue, account,
                logging_queue, status_updates_queue, watchdog_queue
            )
    except InvalidToken:
        messagebox.showerror(
            "Неверный токен", "Проверьте токен, сервер не узнал его."
        )


if __name__ == '__main__':
    with suppress(KeyboardInterrupt, TclError):
        run(main)
