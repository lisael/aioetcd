# Some simple testing tasks (sorry, UNIX only).

FLAGS=


flake:
	flake8 aioetcd tests examples

start_cluster:
	etcd -data-dir=tests.etcd -name=aioetcd_tests &
	sleep 1

shut_cluster:
	kill -15 `pgrep -xf "etcd -data-dir=tests.etcd -name=aioetcd_tests"` || true
	rm -rf tests.etcd

_test:
	nosetests -s $(FLAGS) ./tests/

_vtest:
	nosetests -s -v $(FLAGS) ./tests/

test: flake start_cluster _test shut_cluster

vtest: flake start_cluster _vtest shut_cluster

testloop: start_cluster
	while sleep 1; do python runtests.py $(FLAGS); done
	kill -15 `pgrep -xf "etcd -data-dir=tests.etcd -name=aioetcd_tests"` || true
	rm -rf tests.etcd

_cov:
	nosetests -s --with-cover --cover-html --cover-branches --cover-html-dir ./coverage $(FLAGS) ./tests/
	@echo "open file://`pwd`/coverage/index.html"

cov cover coverage: start_cluster _cov shut_cluster

clean:
	kill -15 `pgrep -xf "etcd -data-dir=tests.etcd -name=aioetcd_tests"` || true
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	rm -rf tests.etcd

doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all build venv flake test vtest testloop cov clean doc start_cluster shut_cluster _test _vtest _cov 
