aioetcd
=======

[![Build Status](https://travis-ci.org/lisael/aioetcd.svg?branch=master)](https://travis-ci.org/lisael/aioetcd)

Coroutine-based etcd client

Asyncio version of https://github.com/jplana/python-etcd 

## Quick start

Install etcd and etcdctl https://github.com/coreos/etcd/blob/master/README.md
(TL;DR? Have a look at `install` section in .travis.yml)

```
virtualenv --python=python3.4 aioetcd
cd aioetcd
git clone https://github.com/lisael/aioetcd.git
cd aioetcd
make vtest # this runs and stops an etcd instance on default ports 4001 and 7001
etcd &
etcdctl set hop 42
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


## Project status

At the moment, the project is still a toy, as it was not battle tested, but it's kind of a big boy's toy. I think it's mature enough to start using it in the real life, but use it carefully. You may have to fork it to fit your needs and expectations (PR, please!).

### Planed features

1. SSL client auth
2. chrooted client (add a directory key prefix to each request )
3. &lt;YOUR WANTED FEATURE HERE (and in an issue, please :) )>

### Known bugs

1. no known bugs
   (which means that the tests **are** buggy)

### Tests

I didn't had time to write an etcd mock, so tests are only integration tests (it needs a working etcd on localhost).

Coverage is about 60% (with emphasis on client.py, where all the gory details are)

## I want to help! What can I do?

Play, fork, hack and, most important, have fun!
