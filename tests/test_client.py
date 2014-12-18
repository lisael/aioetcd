import unittest
import asyncio

from aioetcd.client import Client
from aioetcd import FileNode


class TestClient(unittest.TestCase):
    def test_tests(self):
        pass


class EtcdError(OSError):
    def __init__(self, retcode, stderr):
        OSError.__init__(self, stderr)
        self.retcode = retcode


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
            raise EtcdError(retcode, err.decode('ascii'))
        return out.decode('ascii').rstrip()

    @asyncio.coroutine
    def set(self, key, value):
        yield from self._shell_exec('etcdctl set {} {}'.format(key, value))

    @asyncio.coroutine
    def mkdir(self, key):
        yield from self._shell_exec('etcdctl mkdir {}'.format(key))

    @asyncio.coroutine
    def get(self, key):
        val = yield from self._shell_exec('etcdctl get {}'.format(key))
        return val


class TestRealClient(unittest.TestCase):
    """integration test with a real etcd server"""

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.client = Client(loop=self.loop)

    def test_leader(self):
        leader = self.loop.run_until_complete(self.client.leader())
        self.assertEquals(leader, "http://127.0.0.1:7001")

    def test_machines(self):
        machines = self.loop.run_until_complete(self.client.machines())
        self.assertEquals(machines, ["http://127.0.0.1:4001"])

    @asyncio.coroutine
    def _test_get(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 43)
        node = yield from self.client.get('test1')
        self.assertEquals(node.value, '43')

    def test_get(self):
        self.loop.run_until_complete(self._test_get())

    @asyncio.coroutine
    def _test_get_value(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 42)
        val = yield from self.client.get_value('test1')
        self.assertEquals(val, '42')

    def test_get_value(self):
        self.loop.run_until_complete(self._test_get_value())

    @asyncio.coroutine
    def _test_set(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 43)
        node = yield from self.client.set('test1', 44)
        self.assertTrue(isinstance(node, FileNode))
        val = yield from ctl.get('test1')
        self.assertEquals(val, '44')

    def test_set(self):
        self.loop.run_until_complete(self._test_set())

    @asyncio.coroutine
    def _test_mkdir(self):
        ctl = EtcdController()
        dirname = '/testdir'
        dir_ = yield from self.client.mkdir(dirname)
        yield from ctl.set(dirname + '/file', 42)
        self.assertEquals(dir_.key, dirname)
        self.assertEquals(dir_.ttl, None)
        self.assertEquals(dir_.value, None)
        self.assertEquals(dir_.prev_node, None)
        self.assertEquals(dir_._children, [])

    def test_mkdir(self):
        self.loop.run_until_complete(self._test_mkdir())

    @asyncio.coroutine
    def _test_delete(self):
        ctl = EtcdController()
        yield from ctl.set('test1', 42)
        val = yield from self.client.get_value('test1')
        self.assertEquals(val, '42')
        yield from self.client.delete('test1')
        with self.assertRaisesRegex(EtcdError, r'^Error:\s+100:'):
            yield from ctl.get('test1')

    def test_delete(self):
        self.loop.run_until_complete(self._test_delete())


class TestNodes(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.client = Client(loop=self.loop)

    @asyncio.coroutine
    def _test_updatedir(self):
        ctl = EtcdController()
        dirname = '/testdir2'
        yield from ctl.mkdir(dirname)
        yield from self.client.get(dirname)

    def test_updatedir(self):
        self.loop.run_until_complete(self._test_updatedir())

    @asyncio.coroutine
    def _test_changed(self):
        ctl = EtcdController()
        key = 'test_changed'
        yield from ctl.set(key, "orig")
        node = yield from self.client.get(key)
        changed = yield from node.changed()
        self.assertFalse(changed)
        val = yield from ctl.set(key, 'changed')
        changed = yield from node.changed()
        self.assertTrue(changed)
        val = yield from self.client.get_value(key)
        self.assertEquals(val, "changed")

    def test_changed(self):
        self.loop.run_until_complete(self._test_changed())

    @asyncio.coroutine
    def _test_update(self):
        ctl = EtcdController()
        key = 'test_update'
        yield from ctl.set(key, "orig")
        node = yield from self.client.get(key)
        yield from ctl.set(key, 'changed')
        yield from node.update()
        self.assertEquals(node.value, "changed")

    def test_update(self):
        self.loop.run_until_complete(self._test_update())
