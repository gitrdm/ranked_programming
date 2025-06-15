// ranked_core.i -- SWIG interface file for Nim C API
%module ranked_core
%{
#include "ranked_core.h"
%}

extern int addInts(int a, int b);
extern int alwaysTrue();
