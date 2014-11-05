PYTHON:=python
.PHONY: all
all:
	coffee -b -p -c static/login.coffee > static/login.js
	coffee -b -p -c static/general.coffee > static/general.js

run:
	$(PYTHON) control_server.py
