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
        self.async_results = {}

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

    @asyncio.coroutine
    def _watcher(self, key, index=None, timeout=None):
        yield from self.client.watch(key, index, timeout)
        self.async_results[key] = True

    @asyncio.coroutine
    def _test_watch(self):
        ctl = EtcdController()
        key = 'test_watch'
        yield from ctl.set(key, 42)

        # test a single key
        self.async_results[key] = False
        self.loop.create_task(self._watcher(key))
        for i in range(42):
            yield from asyncio.sleep(0.02)
            self.assertFalse(self.async_results[key])
        yield from ctl.set(key, 42)
        yield from asyncio.sleep(0.001)
        self.assertTrue(self.async_results[key])

        # test with a wait index
        self.async_results[key] = False
        node = yield from self.client.get(key)
        self.loop.create_task(self._watcher(key, node.modifiedIndex + 2))
        yield from asyncio.sleep(0.001)
        yield from ctl.set(key, 42)
        yield from asyncio.sleep(0.001)
        # index is not reached yet, it should not trigger
        self.assertFalse(self.async_results[key])
        yield from ctl.set(key, 42)
        yield from asyncio.sleep(0.001)
        self.assertTrue(self.async_results[key])

        # test timeout
        self.async_results[key] = False
        import time
        start = time.time()
        with self.assertRaises(asyncio.TimeoutError):
            yield from self._watcher(key, timeout=0.2)
        self.assertEquals(int((time.time() - start) * 10), 2)
        self.assertFalse(self.async_results[key])

    @asyncio.coroutine
    def _iterator_watcher(self, key):
        self.async_results[key] = []
        it = yield from self.client.watch_iterator(key)
        for w in it:
            resp = yield from w
            self.async_results[key].append(resp.value)
            if resp.value == '3':
                break

    @asyncio.coroutine
    def _test_watch_iterator(self):
        ctl = EtcdController()
        key = 'test_iterwatch'
        yield from ctl.set(key, 42)

        # test a single key
        self.async_results[key] = False
        self.loop.create_task(self._iterator_watcher(key))
        yield from asyncio.sleep(0.001)
        for i in range(10):
            yield from ctl.set(key, i)
        yield from asyncio.sleep(0.001)
        self.assertEquals(self.async_results[key], ['0', '1', '2', '3'])

    def test_watch_iterator(self):
        self.loop.run_until_complete(self._test_watch_iterator())


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
        yield from asyncio.sleep(0.01)
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

    @asyncio.coroutine
    def _test_prev_node(self):
        key = 'test_prev'
        yield from self.client.set(key, "orig")
        node2 = yield from self.client.set(key, "changed")
        self.assertEquals(node2.value, "changed")

    def test_prev_node(self):
        self.loop.run_until_complete(self._test_prev_node())
