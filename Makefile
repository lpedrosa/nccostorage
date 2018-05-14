ifeq ($(OS),Windows_NT)
	PSC := Powershell -NoProfile -NonInteractive -Command
	RM := $(PSC) Remove-Item -Force -Recurse
	FixPath := $(subst /,\,$1)
else
	RM := rm -rf
	FixPath := $1
endif

run:
	pipenv run python run.py

test:
	pipenv run python -m pytest

lint:
	pipenv run flake8

check: lint test

clean:
	$(RM) *.egg-info
	$(RM) .eggs

.PHONY: run test lint check clean
