gen := ui/UIMain.py ui/UIRunConfig.py ui/UIAbout.py ui/resources_rc.py

all: $(gen)
test: test.c
	gcc -o $@ -g -Og $<
%.py: %.ui
	pyuic4 $< -o $@

%_rc.py: %.qrc
	pyrcc4 $< -o $@

.PHONY: clean cleanall
clean:
	find . -name '*.pyc' -exec rm -f '{}' \;

cleanall: clean
	rm -f ui/UIMain.py ui/UIRunConfig.py
