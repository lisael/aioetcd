aioetcd
=======

Coroutine-based etcd client

asyncio version of https://github.com/jplana/python-etcd 

Only coroutines-based at the moment, I plan to add some callback-style async
(actually, I hate callback style, but sometimes, in python  there is no other
issue)

```
etcd &
etcdctl set hop 42
git clone https://github.com/lisael/aioetcd.git
mkvirtualenv --python=python3.4
cd aioetcd
pip install .
python3.4 example/test_client.py 
```

and in another terminal, run:

```
etcdctl set hello 42
```

to unlock the watch_eternally() coroutine in the example script.

Play, fork, hack and, most important, have fun!
