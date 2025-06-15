# ranking_core_test.nim -- Nim test for basic Ranking class (LAZY version)
import unittest
import ../src/nim_project/ranking_core

test "Ranking construction and toEager (lazy)":
  let r = newRanking(iterator(): RankPair =
    yield (Value(), 0)
    yield (Value(), 1)
    yield (Value(), 2)
  )
  let eager = r.toEager()
  check eager.len == 3
  check eager[0].rank == 0
  check eager[1].rank == 1
  check eager[2].rank == 2

test "Ranking iteration (lazy)":
  let r = newRanking(iterator(): RankPair =
    yield (Value(), 42)
  )
  var found = false
  for pair in r.items:
    check pair.rank == 42
    found = true
  check found

test "Ranking len (lazy)":
  let r = newRanking(iterator(): RankPair =
    yield (Value(), 0)
    yield (Value(), 1)
    yield (Value(), 2)
  )
  check len(r) == 3
  let r_empty = newRanking(iterator(): RankPair = discard)
  check len(r_empty) == 0

test "Ranking isEmpty (lazy)":
  let r = newRanking(iterator(): RankPair =
    yield (Value(), 0)
  )
  check not isEmpty(r)
  let r_empty = newRanking(iterator(): RankPair = discard)
  check isEmpty(r_empty)

test "Ranking string representation (lazy)":
  let r = newRanking(iterator(): RankPair =
    yield (Value(), 0)
    yield (Value(), 1)
    yield (Value(), 2)
  )
  let s = $r
  check s.startsWith("<Ranking:")
  check "3 items" in s
  let r_empty = newRanking(iterator(): RankPair = discard)
  check "0 items" in $r_empty
