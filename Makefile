ifeq ($(OS),Windows_NT)
	PSC := Powershell -NoProfile -NonInteractive -Command
	RM := $(PSC) Remove-Item -Force -Recurse
	FixPath := $(subst /,\,$1)
else
	RM := rm -rf
	FixPath := $1
endif

run:
	python run.py

test:
	python -m pytest

clean:
	$(RM) *.egg-info
	$(RM) .eggs


.PHONY: run test clean
