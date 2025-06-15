## ranking_core.nim -- Core Ranking class for Nim port of ranked programming

# LAZY version with deduplication scaffolding, Design by Contract, and improved documentation
import sets

# A pair of value and rank
# For generality, value is of type 'Value' (generic), rank is int

type
  Value* = ref object
    ## Placeholder for generic value type; can be replaced with a generic type
  RankPair* = tuple[value: Value, rank: int]
    ## A pair of a value and its rank.

  Ranking* = ref object
    ## Ranking: A lazy abstraction for ranked programming.
    ## Wraps a generator/iterator of (value, rank) pairs.
    ## Lazily produces results as needed.
    generator*: iterator(): RankPair ## The underlying generator for this ranking.

# Global deduplication flag (default: enabled)
var globalDedup* = true
  ## If true, deduplicate values in all rankings globally. If false, allow duplicates.

proc setGlobalDedup*(enabled: bool) =
  ## Set the global deduplication flag.
  ## If enabled, duplicate higher-ranked values are filtered out of any ranking that is computed.
  globalDedup = enabled

# Deduplication filter (stub, not yet implemented)
iterator dedupFilter(gen: iterator(): RankPair): RankPair =
  ## Lazily filter out duplicate values from a ranking.
  var seen: HashSet[Value]
  for pair in gen():
    if pair.value notin seen:
      seen.incl(pair.value)
      yield pair
    # else skip duplicate

proc newRanking*(gen: iterator(): RankPair): Ranking =
  ## Construct a new Ranking from a generator iterator.
  ## DbC: gen must not be nil.
  doAssert not gen.isNil, "newRanking: generator must not be nil"
  if globalDedup:
    Ranking(generator: iterator(): RankPair =
      for pair in dedupFilter(gen):
        yield pair
    )
  else:
    Ranking(generator: gen)

iterator items*(r: Ranking): RankPair =
  ## Lazily iterate over (value, rank) pairs in the ranking.
  ## DbC: r must not be nil.
  doAssert not r.isNil, "items: Ranking must not be nil"
  for pair in r.generator():
    yield pair

proc toEager*(r: Ranking): seq[RankPair] =
  ## Materialize all (value, rank) pairs as a seq (eagerly).
  ## DbC: r must not be nil.
  doAssert not r.isNil, "toEager: Ranking must not be nil"
  for pair in r.items:
    result.add(pair)

proc len*(r: Ranking): int =
  ## Return the number of (value, rank) pairs in the ranking (eagerly counts).
  ## DbC: r must not be nil.
  doAssert not r.isNil, "len: Ranking must not be nil"
  for _ in r.items:
    inc result

proc isEmpty*(r: Ranking): bool =
  ## Return true if the ranking is empty (lazily checks first item).
  ## DbC: r must not be nil.
  doAssert not r.isNil, "isEmpty: Ranking must not be nil"
  for _ in r.items:
    return false
  return true

proc `$`*(r: Ranking): string =
  ## Return a string representation of the ranking (shows up to 5 items lazily).
  ## DbC: r must not be nil.
  doAssert not r.isNil, "$: Ranking must not be nil"
  var n = 0
  var preview: seq[string]
  for pair in r.items:
    if n < 5:
      preview.add($pair.rank & ":" & $pair.value)
    inc n
  result = "<Ranking: " & $n & " items; [" & preview.join(", ") & (if n > 5: ", ..." else: "") & "]>"

# Example usage (in doc comment):
# let r = newRanking(iterator(): RankPair =
#   yield (Value(), 0)
#   yield (Value(), 1)
# )
# for pair in r.items:
#   echo pair
# echo len(r)
# echo isEmpty(r)
# echo $r

