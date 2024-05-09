# This file is generated automatically from metadata
# File edits may be overwritten!

.PHONY: upload
upload: metadata package twine add clean

MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(notdir $(patsubst %/,%,$(dir $(MAKEFILE_PATH))))
GUIX-TIME-MACHINE = guix time-machine -C $(MAKEFILE_DIR)/guix/channels.scm
GUIX-SHELL = $(GUIX-TIME-MACHINE) -- shell -f $(MAKEFILE_DIR)/guix/guix.scm
GUIX-DEV-SHELL = $(GUIX-TIME-MACHINE) -- shell -D -f $(MAKEFILE_DIR)/guix/guix.scm
CONTAINER = --container --emulate-fhs --preserve='^DISPLAY$$' --preserve='^TERM$$'
GUIX-CONTAINER = $(GUIX-SHELL) $(CONTAINER)
GUIX-DEV-CONTAINER = $(GUIX-DEV-SHELL) $(CONTAINER)
GUIX-DEV-CONTAINER-NETWORK = $(GUIX-DEV-SHELL) $(CONTAINER) --network
VENV-SHELL = rm -rf .venv && mkdir .venv && python -m venv .venv && source .venv/bin/activate
DOCKER-DEV-IMAGE = docker build -f $(MAKEFILE_DIR)/docker/Dockerfile.dev -t kicad_bom-dev .
DOCKER-DEV-CONTAINER = $(DOCKER-DEV-IMAGE); docker run -it kicad_bom-dev
DOCKER-IMAGE = $(DOCKER-DEV-IMAGE); docker build -f $(MAKEFILE_DIR)/docker/Dockerfile -t kicad_bom .
DOCKER-CONTAINER = $(DOCKER-IMAGE); docker run -it kicad_bom

.PHONY: guix-dev-container
guix-dev-container:
	$(GUIX-DEV-CONTAINER)

.PHONY: guix-dev-container-network
guix-dev-container-network:
	$(GUIX-DEV-CONTAINER-NETWORK)

.PHONY: guix-dev-container-ipython
guix-dev-container-ipython:
	$(GUIX-DEV-CONTAINER) -- ipython --no-autoindent

.PHONY: guix-container
guix-container:
	$(GUIX-CONTAINER) python-ipython --rebuild-cache

.PHONY: requirements.txt
requirements.txt:
	$(GUIX-DEV-CONTAINER-NETWORK) -- sh -c "$(VENV-SHELL) && pip install --trusted-host pypi.org . && pip freeze --local --exclude kicad_bom > requirements.txt && deactivate && rm -rf .venv"

.PHONY: docker-dev-container
docker-dev-container:
	$(DOCKER-DEV-CONTAINER)

.PHONY: docker-dev-container-ipython
docker-dev-container-ipython:
	$(DOCKER-DEV-CONTAINER) ipython --no-autoindent

.PHONY: docker-container
docker-container:
	$(DOCKER-CONTAINER)

.PHONY: metadata-edits
metadata-edits:
	$(GUIX-DEV-CONTAINER) -- sh -c "emacs -q --no-site-file --no-site-lisp --no-splash -l $(MAKEFILE_DIR)/emacs/init.el --file $(MAKEFILE_DIR)/metadata.org"

.PHONY: metadata
metadata:
	$(GUIX-DEV-CONTAINER) -- sh -c "emacs --batch -Q  -l $(MAKEFILE_DIR)/emacs/init.el --eval '(process-org \"$(MAKEFILE_DIR)/metadata.org\")'"

.PHONY: package
package:
	$(GUIX-DEV-CONTAINER) -- sh -c "python3 setup.py sdist bdist_wheel"

.PHONY: twine
twine:
	$(GUIX-DEV-CONTAINER) --network --expose=$$HOME/.pypirc -- sh -c "twine upload dist/*"

.PHONY: add
add:
	$(GUIX-DEV-CONTAINER) -- sh -c "git add --all"

.PHONY: clean
clean:
	$(GUIX-DEV-CONTAINER) -- sh -c "git clean -xdf"
