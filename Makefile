PY_INSTALLER=../PyInstaller-2.1/pyinstaller.py

gen_src := $(wildcard ui/*.ui)
gen_dst := $(gen_src:.ui=.py)

gen_dst += ui/resources_rc.py

all: $(gen_dst)
test: test.c
	gcc -o $@ -g -Og $<

%.py: %.ui
	pyuic4 $< -o $@

UI%.py: %.ui
	pyuic4 $< -o $@

%_rc.py: %.qrc
	pyrcc4 $< -o $@

.PHONY: clean cleanall dist

dist: lll.py
	rm -fr dist
	python2 $(PY_INSTALLER) --hidden-import=uuid --hidden-import=code --hidden-import=codeop -F $<

clean:
	find . -name '*.pyc' -exec rm -f '{}' \;

cleanall: clean
	rm -fr $(gen_dst) dist build

check:
	pylint2 --extension-pkg-whitelist=PyQt4 .
