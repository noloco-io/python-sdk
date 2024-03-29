# python-sdk

## Virtual Python environment

### Creating a virtual environment

When you clone the project for the first time you'll want to setup a Python virtual environment inside the root of the project. This keeps your workspace clean and lets us isolate dependencies across Python projects.

```
$ python3 -m venv env
```

### Working in the virtual environment

Whenever you are working on the project you should enter the virtual environment to make sure that you're in a sterile place to work.

```
$ source env/bin/activate
```

We use `pip3` to manage dependencies and keep track of these in `requirements.txt`.

```
(env) $ pip3 install -r requirements.txt
```

### Exiting the virtual environment

When you are done working on this project you should exit the virtual environment.

```
(env) $ deactivate
```

## Releasing new changes

The SDK is packaged up and distributed on PyPI via `pip`. Right now this process is manual.

Before starting the release proccess, make sure you are in your virtual environment and all dependencies are installed.

Then use `bumpversion` to automatically increment the version number by the part that you want to change.

```
$ bumpversion [major|minor|patch]
```

Now you can build and verify the artifacts that will be uploaded to PyPI.

```
$ python setup.py sdist bdist_wheel
$ twine check dist/*
```

Upload these to TestPyPI and verify that everything looks OK.

```
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Finally upload the package to production PyPI.

```
$ twine upload dist/*
```

You should now be able to get the new version via `pip3`!

```
$ pip3 install noloco
```
