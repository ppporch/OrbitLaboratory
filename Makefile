PDP1_ROOT ?= /opt/pidp1-mods
AM1 ?= $(PDP1_ROOT)/bin/am1
CC ?= cc
BILL_MENU := $(wildcard $(PDP1_ROOT)/Am1Includes/PENMENU/* $(PDP1_ROOT)/Am1Includes/memory.ah)
DEPS := $(wildcard src/*.ac src/*.am1 p1gl/src/* p1gl/generated/* generated/* ui/*)
.PHONY: all test
all: build/orbit.rim
build:
	mkdir -p build
build/orbit.rim: $(DEPS) $(BILL_MENU) generated/force.ac generated/outlines.ac generated/instrument-text.ac | build
	cd build && $(AM1) -d -S ../src/orbit.am1
generated/force.ac generated/outlines.ac generated/instrument-text.ac &: tools/generate.py
	python3 tools/generate.py
build/runner: tests/runner.c $(PDP1_ROOT)/src/pdp1/pdp1.o | build
	$(CC) -O2 -DP1GL_TYPE340_TEST -DRUNNER_CYCLE_LIMIT=20000000 -I$(PDP1_ROOT)/src/pdp1 -I$(PDP1_ROOT)/src/common -o $@ $< $(PDP1_ROOT)/src/pdp1/pdp1.o -lm
test: all build/runner
	AM1=$(AM1) python3 tests/test_orbit.py
	AM1=$(AM1) python3 tests/test_instruments.py
	AM1=$(AM1) python3 tests/test_menu.py

.PHONY: run
run: all
	$(PDP1_ROOT)/bin/fastload -y build/orbit.rim
