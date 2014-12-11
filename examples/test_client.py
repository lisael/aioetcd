import asyncio
import aioetcd.client

@asyncio.coroutine
def print_leader():
    client = aioetcd.client.Client()
    result = yield from client.leader()
    print(result)

@asyncio.coroutine
def client_set(key, value):
    client = aioetcd.client.Client()
    result = yield from client.set(key, value)
    print(result)

@asyncio.coroutine
def client_get(key):
    client = aioetcd.client.Client()
    result = yield from client.get(key)
    print(result)

@asyncio.coroutine
def print_machines():
    client = aioetcd.client.Client()
    result = yield from client.machines()
    print(result)

@asyncio.coroutine
def watch_eternally():
    client = aioetcd.client.Client(read_timeout=2, allow_reconnect=True)
    result = yield from client.watch('hello')
    print(result)

@asyncio.coroutine
def watch_timeout():
    client = aioetcd.client.Client(read_timeout=2, allow_reconnect=True)
    result = yield from client.watch('hello', timeout=5)
    print(result)

@asyncio.coroutine
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(print_leader())
    loop.create_task(print_machines())
    loop.create_task(client_set('hop', 42))
    loop.create_task(client_get('hop'))
    yield from watch_eternally()
    yield from watch_timeout()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

