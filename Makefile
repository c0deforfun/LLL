PY_INSTALLER=../PyInstaller-2.1/pyinstaller.py

gen := ui/UIMain.py ui/UIRunConfig.py ui/UIAbout.py ui/resources_rc.py

all: $(gen)
test: test.c
	gcc -o $@ -g -Og $<
%.py: %.ui
	pyuic4 $< -o $@

%_rc.py: %.qrc
	pyrcc4 $< -o $@

.PHONY: clean cleanall dist

dist: lll.py
	$(PY_INSTALLER) -F --hidden-import=uuid --hidden-import=code --hidden-import=codeop $<


clean:
	find . -name '*.pyc' -exec rm -f '{}' \;

cleanall: clean
	rm -f $(gen) dist build
