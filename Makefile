flake:
	flake8 sage_utils tests

develop:
	python setup.py develop

test:
	py.test -q -s --cov sage_utils --cov-report term-missing --tb=native
