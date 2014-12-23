#Author: Richard Torenvliet
#Github alias: icyrizard

VATIC_NAME=vaticdev

check:
	pep8 .
	pyflakes .
	echo "success"


# should be called once, but it's be allowed to be called multiple times.
bootstrap:
	fig run $(VATIC_NAME) bash -c "/scripts/bootstrap.sh $(VATIC_NAME)"

# remove, build and run the image
run:
	fig rm --force $(VATIC_NAME); fig build && fig up

build:
	fig rm --force $(VATIC_NAME); fig build
