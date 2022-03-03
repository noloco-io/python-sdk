# python-sdk

## Creating a Virtual Environment

When you clone the project for the first time you'll need to setup a Python virtual environment inside the root of the project. This keeps your workspace clean and lets us isolate dependencies across Python projects.

```
$ python3 -m venv env
```

## Working in the Virtual Environment

Whenever you are working on the project you should enter the virtual environment to make sure that you're in a sterile place to work.

```
$ source env/bin/activate
```

We use `pip3` to manage dependencies.

```
(env) $ pip3 install -r requirements.txt
```

## Exiting the Virtual Environment

When you are done working on this project you should exit the virtual environment.

```
(env) $ deactivate
```
