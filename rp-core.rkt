#lang racket

;; =============================================================================
;; Ranked Programming Core Library (Literate Documentation)
;; =============================================================================
;; This file implements the core data structures and combinators for ranked
;; programming in Racket. It provides lazy ranking chains, merging, joining,
;; mapping, filtering, deduplication, and conversion utilities for probabilistic
;; and ranked search programming.
;;
;; Concepts:
;; - A "ranking" is a lazy chain of elements, each with a value, a rank (cost),
;;   and a promise for the next element.
;; - All combinators are lazy and work with promises (delayed computations).
;; - The chain ends with a special terminal element.
;;
;; Example Usage:
;;   (define r (delay (element (delay 'a) 0
;;                             (delay (element (delay 'b) 1 terminate-promise)))))
;;   (define r2 (map-value symbol->string r))
;;   (define r3 (merge r r2))
;;   (convert-to-assoc r3) ; => (("a" . 0) ("b" . 1) ...)
;; =============================================================================

(require racket/match)
(provide (all-defined-out))
(require srfi/1)

;; -----------------------------------------------------------------------------
;; Ranking Element Structure and Accessors
;; -----------------------------------------------------------------------------
;; A ranking element is a list: (value-promise rank successor-promise)
;; - value-promise: a promise for the value at this node
;; - rank: a non-negative real number (or +inf.0 for terminal)
;; - successor-promise: a promise for the next ranking element

; Return the value captured (as value-promise) in a given ranking element.
(define value (lambda (x) (force (car x))))

; Return value-promise stored in a given ranking element.
(define value-promise car)

; Return rank stored in a given ranking element.
(define rank cadr)

; Return successor element-promise stored in a given ranking element.
(define successor-promise caddr)

; Return successor ranking element stored (as element-promise) in a given ranking element.
(define successor (lambda (x) (force (caddr x))))

; Create a new ranking element with given value-promise, rank, and successor-promise.
(define (element value-promise rank successor-promise)
  "Construct a ranking element node."
  (list value-promise rank successor-promise))

; Return element-promise that captures the terminal ranking element.
(define terminate-promise
  (delay terminate-element))

; The terminal element (marks end of ranking function chain).
(define terminate-element
  (element (delay 0) +inf.0 terminate-promise))

;; -----------------------------------------------------------------------------
;; Core Combinators: Mapping, Filtering, Normalization, Shifting
;; -----------------------------------------------------------------------------

; map-value : (a -> b) rf -> ranking
; Create new ranking by applying f to each value in rf.
(define (map-value f rf)
   (delay
    (let ((res (force rf)))
      (if (infinite? (rank res))
          terminate-element
          (element
           (delay (f (value res)))
           (rank res)
           (map-value f (successor-promise res)))))))

; map-value-promise : (promise -> promise) rf -> ranking
; Like map-value, but f takes a value promise and returns a value promise.
(define (map-value-promise f rf)
   (delay
    (let ((res (force rf)))
      (if (infinite? (rank res))
          terminate-element
          (element
           (f (value-promise res))
           (rank res)
           (map-value-promise f (successor-promise res)))))))

; normalise : ranking [start-rank] -> ranking
; Normalize all ranks in rf so the first element has rank 0.
(define (normalise rf [s #f])
  (delay
    (let ((res (force rf)))
      (if (infinite? (rank res))
          terminate-element
          (element
           (value-promise res)
           (if s (- (rank res) s) 0)
           (normalise (successor-promise res)
                      (if s s (rank res))))))))

; shift : number ranking -> ranking
; Add n to all ranks in rf.
(define (shift n rf)
  (delay
    (let ((res (force rf)))
      (if (infinite? (rank res))
          terminate-element
          (element
           (value-promise res)
           (+ (rank res) n)
           (shift n (successor-promise res)))))))

; filter-ranking : (a -> bool) ranking -> ranking
; Keep only elements where pred(value) is true.
(define (filter-ranking pred rf)
  (delay
    (let ((res (force rf)))
      (if (infinite? (rank res))
          terminate-element
          (if (pred (value res))
              (element
               (value-promise res)
               (rank res)
               (filter-ranking pred (successor-promise res)))
              (force (filter-ranking pred (successor-promise res))))))))
              
; filter-after : int ranking -> ranking
; Only pass through first n elements.
(define (filter-after n rf)
  (if (= n 0)
      terminate-promise
      (delay
        (let ((res (force rf)))
          (if (infinite? (rank res))
              terminate-element
              (element
               (value-promise res)
               (rank res)
               (filter-after (- n 1) (successor-promise res))))))))

; up-to-rank : number ranking -> ranking
; Only pass through elements with rank <= r.
(define (up-to-rank r rf)
  (delay
    (let ((res (force rf)))
      (if (> (rank res) r)
          terminate-element
          (element
           (value-promise res)
           (rank res)
           (up-to-rank r (successor-promise res)))))))

; do-with : ranking (element -> void) -> void
; For each element, call f with the element as argument.
(define (do-with rf f)
  (let ((res (force rf)))
    (when (not (infinite? (rank res)))
      (begin
        (f res)
        (do-with (successor-promise res) f)))))

;; -----------------------------------------------------------------------------
;; Merging and Joining Rankings
;; -----------------------------------------------------------------------------
;; merge : ranking ranking [start-rank] -> ranking
;; Merge two ranking functions, preserving order by rank. If two elements have the same rank,
;; the element from the first ranking is preferred. This is a lazy, recursive merge.
(define (merge rfa rfb [sr 0])
   (delay
    (let ((resa (force rfa)))
      (if (= (rank resa) sr)
          (element
           (value-promise resa)
           (rank resa)
           (merge (successor-promise resa) rfb sr))
          (let ((resb (force rfb)))
            (if (<= (rank resa) (rank resb))
                (element
                 (value-promise resa)
                 (rank resa)
                 (merge (successor-promise resa) (delay resb) (rank resa)))
                (element
                 (value-promise resb)
                 (rank resb)
                 (merge (delay resa) (successor-promise resb) (rank resb)))))))))
         
;; merge-list : (list ranking) -> ranking
;; Merge a list of ranking functions into a single ranking, preserving rank order.
(define (merge-list rf-list)
  (if (= (length rf-list) 1)
      (car rf-list)
      (merge
       (car rf-list)
       (merge-list (cdr rf-list)))))

;; join : ranking ranking -> ranking
;; Join two ranking functions, producing a ranking of pairs (as lists).
(define (join rfa rfb)
  (merge-apply rfa (λ (va) (map-value (λ (b) (list va b)) rfb))))

;; join-list : (list ranking) -> ranking
;; Join a list of ranking functions, producing a ranking of tuples (as lists).
(define (join-list rf-list)
  (cond
    [(empty? rf-list) terminate-promise]
    [(= (length rf-list) 1) (map-value list (car rf-list))]
    [(= (length rf-list) 2) (join (first rf-list) (second rf-list))]
    [else (map-value
           (λ (x) (cons (first x) (second x)))
           (join (first rf-list) (join-list (cdr rf-list))))]))

;; -----------------------------------------------------------------------------
;; Advanced Merging
;; -----------------------------------------------------------------------------
;; merge-apply : ranking (a -> ranking) -> ranking
;; For each value in rfs, apply f and merge the resulting rankings, shifting ranks.
;; This is a key combinator for higher-order ranked programming.
(define (merge-apply rfs f)
   (delay
    (let ((res (force rfs)))
      (if (infinite? (rank res))
          terminate-element
          (force
           (let ((res2 (successor res)))
             (merge-with-ranks
              (shift (rank res) (f (value res)))
              (rank res)
              (merge-apply (delay res2) f)
              (rank res2))))))))

;; merge-with-ranks : ranking number ranking number -> ranking
;; Merge two rankings, given their current ranks. Used internally by merge-apply.
(define (merge-with-ranks rfa ra rfb rb)
  (cond
    [(and (infinite? ra) (infinite? rb)) terminate-promise]
    [(infinite? ra) rfb]
    [(infinite? rb) rfa]
    [(<= ra rb)
     (delay
       (let ((resa (force rfa)))
         (element
          (value-promise resa)
          (rank resa)
          (delay
            (let ((resa2 (successor resa)))
              (force (merge-with-ranks (delay resa2) (rank resa2) rfb rb)))))))]
     [else
      (delay
        (let ((resb (force rfb)))
          (element
           (value-promise resb)
           (rank resb)
           (delay
             (let ((resb2 (successor resb)))
               (force (merge-with-ranks rfa ra (delay resb2) (rank resb2))))))))]))

;; -----------------------------------------------------------------------------
;; Correctness, Deduplication, and Conversion Utilities
;; -----------------------------------------------------------------------------

; check-correctness : ranking [prev-rank] -> ranking
; Check that the ranking is in non-decreasing rank order.
(define (check-correctness rf [c -1])
  (delay
    (let ((res (force rf)))
      (if (and (infinite? (rank res)) (= c -1))
          res
          (if (>= (rank res) c)
              (element (value-promise res)
                       (rank res)
                       (check-correctness (successor-promise res) (rank res)))
              (error "incorrect rank order" c (rank res)))))))

; dedup : ranking [set] -> ranking
; Remove duplicate values, keeping only the lowest-rank occurrence.
(define global-dedup-enabled #T)
(define (set-core-global-dedup x) (set! global-dedup-enabled x))

(define (dedup rf [s (set)])
  (if (not global-dedup-enabled)
      rf
      (delay
        (let ((res (force rf)))
          (if (infinite? (rank res))
              terminate-element
              (if (set-member? s (value res))
                  (force (dedup (successor-promise res) s))
                  (element (value-promise res)
                           (rank res)
                           (dedup (successor-promise res) (set-add s (value res))))))))))

; convert-to-hash : ranking -> hash
; Convert a ranking to a hash table mapping value to rank.
(define (convert-to-hash rf)
  (letrec
      ((fill-hash
        (λ (rf table)
          (let ((res (force rf)))
            (when (not (infinite? (rank res)))
              (begin
                (when (not (hash-has-key? table (value res)))
                  (hash-set! table (value res) (rank res)))
                (fill-hash (successor-promise res) table))))))
       (tab (make-hash)))
    (fill-hash rf tab) tab))

; convert-to-assoc : ranking -> (list (cons value rank))
; Convert a ranking to an association list of (value . rank) pairs.
(define (convert-to-assoc rf)
  (let ((res (force rf)))
    (if (infinite? (rank res))
        `()
        (cons (cons (value res) (rank res)) (convert-to-assoc (successor-promise res))))))

; convert-to-stream : ranking -> stream
; Convert a ranking to a stream of (value . rank) pairs.
(define (convert-to-stream rf)
  (let ((res (force rf)))
    (if (infinite? (rank res))
        empty-stream
        (stream-cons (cons (value res) (rank res)) (convert-to-stream (successor-promise res))))))

; construct-from-assoc : (list (cons value rank)) -> ranking
; Construct a ranking from an association list of (value . rank) pairs.
(define (construct-from-assoc assoc-list)
  (delay
    (if (empty? assoc-list)
        terminate-element
        (element
         (delay (caar assoc-list))
         (cdar assoc-list)
         (construct-from-assoc (cdr assoc-list))))))

;; =============================================================================
;; End of Ranked Programming Core Library
;; =============================================================================
