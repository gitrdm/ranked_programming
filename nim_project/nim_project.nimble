# nim_project.nimble

version       = "0.1.0"
author        = "rdmerrio"
description   = "A test library project"
license       = "MIT"
srcDir        = "src"

requires "nim >= 2.0.0"

skipFiles = @["ranked_core.nim", "test.nim"]

# This defines a custom build task named "make"
task make, "Builds the shared library":
  let flags = @[
    "--app:lib",
    "-d:release",
    "--noMain",
    "--header:capi/libranked_core.h",
    "--out:lib/libranked_core.so"
  ]
  
  let command = "nim c " & flags.join(" ") & " src/nim_project/ranked_core.nim"
  
  echo "Executing build command: ", command
  exec command