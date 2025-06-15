# test.nim
proc addInts*(a, b: cint): cint {.exportc.} =
  result = a + b