.PHONY: tests docs

tests:
	coverage run -m unittest discover
	coverage report

docs:
	rm -rf ./docs/_build
	cd docs; make html

clean:
	rm -rf ./docs/_build
