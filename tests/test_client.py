import unittest
import asyncio

from aioetcd.client import Client


class TestClient(unittest.TestCase):
    def test_tests(self):
        pass


class EtcdError(OSError):
    pass


class EtcdController:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def _shell_exec(self, cmd):
        shell = asyncio.create_subprocess_shell(
            cmd, stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        proc = yield from shell
        out, err = yield from proc.communicate()
        retcode = yield from proc.wait()
        if retcode:
            raise EtcdError()
        return out.decode('ascii').rstrip()

    @asyncio.coroutine
    def set(self, key, value):
        yield from self._shell_exec('etcdctl set {} {}'.format(key, value))

    @asyncio.coroutine
    def get(self, key):
        val = yield from self._shell_exec('etcdctl get {}'.format(key))
        return val


class TestRealClient(unittest.TestCase):
    """integration test with a real etcd server"""

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.client = Client(loop=self.loop)

    def tearDown(self):
        pass

    def test_leader(self):
        leader = self.loop.run_until_complete(self.client.leader())
        self.assertEquals(leader, "http://127.0.0.1:7001")

    def test_machines(self):
        machines = self.loop.run_until_complete(self.client.machines())
        self.assertEquals(machines, ["http://127.0.0.1:4001"])

    @asyncio.coroutine
    def _test_get(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 42)
        val = yield from self.client.get('test1')
        self.assertEquals(val, '42')

    def test_get(self):
        self.loop.run_until_complete(self._test_get())

    @asyncio.coroutine
    def _test_set(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 43)
        yield from asyncio.sleep(0.3)
        yield from self.client.set('test1', 44)
        yield from asyncio.sleep(0.3)
        val = yield from ctl.get('test1')
        self.assertEquals(val, '44')

    def test_set(self):
        self.loop.run_until_complete(self._test_set())
