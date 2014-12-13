import asyncio
import aioetcd.client


@asyncio.coroutine
def print_leader():
    print('print_leader')
    client = aioetcd.client.Client()
    result = yield from client.leader()
    print(result)


@asyncio.coroutine
def client_set(key, value):
    print('client_set')
    client = aioetcd.client.Client()
    result = yield from client.set(key, value)
    print(result)


@asyncio.coroutine
def client_get(key):
    print('client_get')
    client = aioetcd.client.Client()
    result = yield from client.get(key)
    print(result)


@asyncio.coroutine
def print_machines():
    print('print_machine')
    client = aioetcd.client.Client()
    result = yield from client.machines()
    print(result)


@asyncio.coroutine
def watch_eternally(key):
    print('watch_eternally')
    client = aioetcd.client.Client(read_timeout=2, allow_reconnect=True)
    result = yield from client.watch(key)
    print(result)


@asyncio.coroutine
def watch_timeout(key):
    print('watch_timeout')
    client = aioetcd.client.Client(read_timeout=2, allow_reconnect=True)
    result = yield from client.watch(key, timeout=5)
    print(result)


@asyncio.coroutine
def watch_forever(key):
    print('watch_forever')
    client = aioetcd.client.Client(read_timeout=5, allow_reconnect=True)
    it = yield from client.watch_iterator(key)
    for watcher in it:
        resp = yield from watcher
        print(resp.value)
        if resp.value == '42':
            break


@asyncio.coroutine
def main():
    print('---------------------')
    yield from print_leader()
    print('---------------------')
    yield from print_machines()
    print('---------------------')
    yield from client_set('hello', 43)
    print('---------------------')
    yield from client_get('hello')
    print('---------------------')
    # run :
    #    etcdctl set hello 0
    # a couple of time and then
    #    etcdctl set hello 42
    # as soon as it becomes boring
    yield from watch_forever('hello')
    print('---------------------')
    # run :
    #    etcdctl set hello 0
    # to unlock
    yield from watch_eternally("hello")
    print('---------------------')
    # run :
    #    etcdctl set hello 0
    # or wait 5 seconds to unlock
    yield from watch_timeout('hello')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
