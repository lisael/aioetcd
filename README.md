aioetcd
=======

[![Build Status](https://travis-ci.org/lisael/aioetcd.svg)](https://travis-ci.org/lisael/aioetcd)

Coroutine-based etcd client

asyncio version of https://github.com/jplana/python-etcd 

Only coroutines-based at the moment, I plan to add some callback-style async
(actually, I hate callback style, but sometimes, in python  there is no other
way)

## Quick start

install etcd and etcdctl ( https://github.com/coreos/etcd/blob/master/README.md )

```
etcd &
etcdctl set hop 42
git clone https://github.com/lisael/aioetcd.git
virtualenv --python=python3.4 aioetcd
cd aioetcd
pip install .
python3.4 example/simple_client.py 
```

and in another terminal, run:

```
etcdctl set hello 0 # a couple of time and then
etcdctl set hello 42 # as soon as it becomes boring
etcdctl set hello 42 # or wait 5 seconds to unlock
```

(read the script to see what's going on)


Play, fork, hack and, most important, have fun!
