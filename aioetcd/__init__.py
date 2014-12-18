import asyncio


class Node:
    _node_props = {
        'key': None,
        'value': None,
        'expiration': None,
        'ttl': None,
        'modifiedIndex': None,
        'createdIndex': None,
        '_prev_node': None
    }
    """Base class for etcd nodes. Cannot be instanciated"""
    def __new__(cls, **kwargs):
        # sometimes the write response of a dir is bogus, we have to check
        # the prevNode to be sure it's not a dir
        node = kwargs.get('node', {})
        if node.pop("dir", False) or kwargs.get(
                "prevNode", {}).get("dir", False):
            return super(Node, cls).__new__(DirNode)
        else:
            return super(Node, cls).__new__(FileNode)

    def __init__(self, **kwargs):
        self.__dict__ = dict(self._node_props)
        self._update_from_dict(**kwargs)

    def _update_from_dict(self, **kwargs):
        node = kwargs.pop('node', {})
        self._prev_node = kwargs.pop('prevNode', None)
        self.__dict__.update(kwargs)
        self.__dict__.update(node)

    @asyncio.coroutine
    def update(self):
        resp = yield from self.client._read_headers(self.key)
        params = yield from self.client._decode_response(resp)
        self._update_from_dict(**params)

    @property
    def prev_node(self):
        if isinstance(self._prev_node, dict):
            self._prev_node = Node(**self._prev_node)
        return self._prev_node

    @asyncio.coroutine
    def changed(self):
        params = dict(wait=True, waitIndex=self.modifiedIndex + 1)
        head = yield from self.client._read_headers(self.key, None, **params)
        content = head.content.read_nowait()
        head.close(force=True)
        return bool(content)


class FileNode(Node):
    def __init__(self, **kwargs):
        super(FileNode, self).__init__(**kwargs)


class DirNode(Node):
    def __new__(cls, **kwargs):
        kwargs['dir'] = True
        return super(Node, cls).__new__(DirNode, **kwargs)

    def __init__(self, **kwargs):
        super(DirNode, self).__init__(**kwargs)
        self._children = kwargs.get("nodes", [])

    def _update_from_dict(self, **kwargs):
        kwargs['_children'] = kwargs.pop('nodes', None)
        super(DirNode, self)._update_from_dict(**kwargs)

    def __iter__(self):
        for child in self._children:
            yield Node(child)

    @asyncio.coroutine
    def iter_children(self, update=False):
        if self._children is None:
            yield from self.update()
        elif update:
            changed = yield from self.changed()
            if changed:
                yield from self.update()
        return iter(self)


class EtcdException(Exception):
    """
    Generic Etcd Exception.
    """
    pass


class EtcdError:
    # See https://github.com/coreos/etcd/blob/master/Documentation/errorcode.md
    """
    const (
    EcodeKeyNotFound    = 100
    EcodeTestFailed     = 101
    EcodeNotFile        = 102
    EcodeNoMorePeer     = 103
    EcodeNotDir         = 104
    EcodeNodeExist      = 105
    EcodeKeyIsPreserved = 106
    EcodeRootROnly      = 107

    EcodeValueRequired     = 200
    EcodePrevValueRequired = 201
    EcodeTTLNaN            = 202
    EcodeIndexNaN          = 203

    EcodeRaftInternal = 300
    EcodeLeaderElect  = 301

    EcodeWatcherCleared = 400
    EcodeEventIndexCleared = 401
    )

    // command related errors
    errors[100] = "Key Not Found"
    errors[101] = "Test Failed" //test and set
    errors[102] = "Not A File"
    errors[103] = "Reached the max number of peers in the cluster"
    errors[104] = "Not A Directory"
    errors[105] = "Already exists" // create
    errors[106] = "The prefix of given key is a keyword in etcd"
    errors[107] = "Root is read only"

    // Post form related errors
    errors[200] = "Value is Required in POST form"
    errors[201] = "PrevValue is Required in POST form"
    errors[202] = "The given TTL in POST form is not a number"
    errors[203] = "The given index in POST form is not a number"

    // raft related errors
    errors[300] = "Raft Internal Error"
    errors[301] = "During Leader Election"

    // etcd related errors
    errors[400] = "watcher is cleared due to etcd recovery"
    errors[401] = "The event in requested index is outdated and cleared"
    """

    error_exceptions = {
        100: KeyError,
        101: ValueError,
        102: KeyError,
        103: Exception,
        104: KeyError,
        105: KeyError,
        106: KeyError,
        200: ValueError,
        201: ValueError,
        202: ValueError,
        203: ValueError,
        300: Exception,
        301: Exception,
        400: Exception,
        401: EtcdException,
        500: EtcdException
    }

    @classmethod
    def handle(cls, errorCode=None, message=None, cause=None, **kwdargs):
        """ Decodes the error and throws the appropriate error message"""
        try:
            msg = "{} : {}".format(message, cause)
            exc = cls.error_exceptions[errorCode]
        except:
            msg = "Unable to decode server response"
            exc = EtcdException
        raise exc(msg)
