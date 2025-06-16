CARGO ?= cargo
PROTOC ?= protoc

.PHONY: build run test proto

build:
	$(CARGO) build

run:
	$(CARGO) run

test:
	$(CARGO) test

proto:
	$(PROTOC) --rust_out=src --proto_path=proto proto/*.proto
