# Makefile for Nim -> C -> SWIG -> Python pipeline

NIM_SRC=src/ranked_core.nim
NIM_LIB=lib/libranked_core.so
NIMBLE=nimble
SWIG_I=capi/ranked_core.i
SWIG_H=capi/ranked_core.h
SWIG_C=build/ranked_core_wrap.c
SWIG_O=build/ranked_core_wrap.o
PY_MOD=build/_ranked_core.so
PY_INC=/usr/include/python3.10
CAPI_DIR=capi
BUILD_DIR=build
LIB_DIR=lib

.PHONY: all clean test build_and_test

all: $(PY_MOD)

test:
	pytest

build_and_test: all test

$(NIM_LIB): $(NIM_SRC)
	$(NIMBLE) make

$(SWIG_C): $(SWIG_I) $(SWIG_H)
	swig -python -outdir $(BUILD_DIR) -o $(SWIG_C) $(SWIG_I)

$(SWIG_O): $(SWIG_C) $(SWIG_H)
	gcc -fPIC -c $(SWIG_C) -I$(PY_INC) -I$(CAPI_DIR) -o $(SWIG_O)

$(PY_MOD): $(NIM_LIB) $(SWIG_O)
	gcc -shared -fPIC $(SWIG_O) $(NIM_LIB) -o $(PY_MOD) -L$(LIB_DIR) -Wl,-rpath,$(LIB_DIR)

clean:
	rm -rf $(BUILD_DIR)/*.o $(BUILD_DIR)/*.so $(BUILD_DIR)/*_wrap.c $(BUILD_DIR)/*.py $(LIB_DIR)/*.so nimcache capi/libranked_core.h