PY_INSTALLER=../PyInstaller-2.1/pyinstaller.py

gen := ui/UIMain.py ui/UIRunConfig.py ui/UIAbout.py ui/resources_rc.py ui/UISourceFileTreeWidget.py ui/UIValueViewerWidget.py

all: $(gen)
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
	rm -f $(gen) dist build
