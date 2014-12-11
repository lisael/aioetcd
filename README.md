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
pip install -r requirements.txt # only aiohttp
cd aioetcd
cp examples/test_client.py .
python3.4 test_client.py 
# yes, I need a setup.py. I know
```

and in another terminal, run:

```
etcdctl set hello 42
```

to unlock the watch_eternally() in the example script.

Play, fork, hack and, most important, have fun!
