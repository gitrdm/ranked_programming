# ranked_core.nim -- minimal Nim module with C-exported function for SWIG demo

proc addInts(a, b: cint): cint {.exportc, dynlib.} =
  ## Simple demo function to test Nim->C->SWIG->Python pipeline
  return a + b
