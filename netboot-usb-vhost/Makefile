# Makefile for creating and cleaning up a custom ISO
#
# STOCK_ISO: Specify the path to a Debian 13 netboot USB ISO.

# Default target
.PHONY: all
all: build

# Build target
.PHONY: build
build: clean
	@if [ -z "$(STOCK_ISO)" ]; then \
	  echo "Error: STOCK_ISO is required."; \
	  echo "Please specify the path to a Debian 13 (Trixie) netboot USB ISO."; \
	  exit 1; \
	fi
	mkdir -p log
	mkdir -p tmp
	./create_iso.py

# clean target
.PHONY: clean
clean:
	chmod +w -R tmp/* || true
	rm -rf tmp/*
	rm -rf tmp/.disk
	rm -rf log/*
	rm -f custom.iso
	rm -f *.cfg
