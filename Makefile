.PHONY: tests docs

tests:
	python -m unittest

docs:
	rm -rf ./docs/_build
	cd docs; make html

clean:
	rm -rf ./docs/_build
