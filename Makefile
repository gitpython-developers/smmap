.PHONY: build sdist cover test clean-files clean-docs doc all  

all:
	$(info Possible targets:)
	$(info doc)
	$(info clean-docs)
	$(info clean-files)
	$(info clean)
	$(info test)
	$(info coverage)
	$(info build)
	$(info sdist)

doc:
	cd docs && make html

clean-docs:
	cd docs && make clean

clean-files:
	git clean -fx

clean: clean-files clean-docs

test:
	nosetests

coverage:
	nosetests --with-coverage --cover-package=smmap
	
build:
	./setup.py build
	
sdist:
	./setup.py sdist


