#lang racket

;; =============================================================================
;; Ranked Programming API Layer (Literate Documentation)
;; =============================================================================
;; This file provides the public API for the ranked programming library in Racket.
;; It re-exports core combinators, defines user-facing macros, and provides
;; documentation for all exported functions and macros. This file is written in
;; a literate programming style, with detailed comments and type annotations
;; where possible.
;;
;; Concepts:
;; - A "ranking" is a lazy chain of elements, each with a value, a rank (cost),
;;   and a promise for the next element.
;; - The API provides combinators for constructing, transforming, and querying
;;   rankings, as well as utilities for display and deduplication.
;;
;; Type Annotations:
;; - Racket does not enforce static types by default, but we provide type
;;   contracts and comments for clarity. Where possible, contracts are used.
;; =============================================================================

(require racket/match)
(require racket/format)
(require srfi/1)
(require "rp-core.rkt")

(provide
 ranking? ; (Any) -> Boolean
 rank?    ; (Any) -> Boolean
 ranking/c ; contract for rankings
 rank/c    ; contract for ranks
 construct-ranking ; macro: (construct-ranking (v . r) ...) -> ranking
 nrm/exc   ; macro: (nrm/exc v1 v2 [rank]) -> ranking
 !         ; (Any) -> ranking
 failure   ; () -> ranking
 either-of ; (Listof Any) -> ranking
 either/or ; macro: (either/or v ...) -> ranking
 observe   ; ((Any -> Boolean) ranking) -> ranking
 observe-r ; (Rank (Any -> Boolean) ranking) -> ranking
 observe-e ; (Rank (Any -> Boolean) ranking) -> ranking
 cut       ; (Rank ranking) -> ranking
 limit     ; (Nat ranking) -> ranking
 rank-of   ; ((Any -> Boolean) ranking) -> Rank
 $         ; (Function | ranking Function | ranking ...) -> ranking
 rlet      ; macro: (rlet ((var expr) ...) body ...) -> ranking
 rlet*     ; macro: (rlet* ((var expr) ...) body ...) -> ranking
 rf-equal? ; (ranking ranking) -> Boolean
 rf->hash  ; (ranking) -> HashTable
 rf->assoc ; (ranking) -> (Listof (Pair Any Rank))
 rf->stream; (ranking) -> Stream
 pr-all    ; (ranking) -> Void
 pr-until  ; (Rank ranking) -> Void
 pr-first  ; (Nat ranking) -> Void
 pr        ; (ranking) -> Void
 set-global-dedup ; (Boolean) -> Void
)

;; -----------------------------------------------------------------------------
;; Internal marker for ranking functions
;; -----------------------------------------------------------------------------
(define rf-marker `ranking-function)

;; -----------------------------------------------------------------------------
;; Autocast: Convert values to ranking chains
;; -----------------------------------------------------------------------------
;; autocast : Any -> ranking-chain
;; If the value is a ranking, force it; otherwise, wrap as singleton ranking.
(define autocast
  (lambda (value)
    (if (ranking? value)
        (force (cdr value))
        (element (delay value) 0 terminate-promise))))

;; -----------------------------------------------------------------------------
;; Predicates and Contracts
;; -----------------------------------------------------------------------------
;; ranking? : Any -> Boolean
;; Returns #t if value is a ranking function.
(define (ranking? value) (and (pair? value) (eq? (car value) rf-marker)))

;; ranking/c : contract for rankings
(define ranking/c
  (flat-named-contract 'ranking/c ranking?))

;; rank? : Any -> Boolean
;; Returns #t if value is a non-negative integer or +inf.0.
(define (rank? x) (or (exact-nonnegative-integer? x) (infinite? x)))

;; rank/c : contract for ranks
(define rank/c
  (flat-named-contract 'rank/c rank?))

;; one-arg-proc? : Any -> Boolean
;; Returns #t if proc is a procedure of arity 1.
(define (one-arg-proc? proc) (and (procedure? proc) (procedure-arity-includes? proc 1)))

;; mark-as-rf : ranking-chain -> ranking
(define (mark-as-rf rf) (cons rf-marker rf))

;; -----------------------------------------------------------------------------
;; Empty and Failure Rankings
;; -----------------------------------------------------------------------------
;; terminate-rf : ranking
(define terminate-rf (mark-as-rf terminate-promise))

;; failure : -> ranking
;; Returns the empty ranking.
(define (failure) terminate-rf)

;; -----------------------------------------------------------------------------
;; Construction Macros
;; -----------------------------------------------------------------------------
;; construct-ranking : macro
;; Usage: (construct-ranking (v . r) ...)
;; Constructs a ranking from association pairs.
(define-syntax construct-ranking 
  (syntax-rules ()
    ((construct-ranking a ...)
     (mark-as-rf
      (check-correctness
       (construct-from-assoc `(a ...)))))))

;; ! : Any -> ranking
;; Truth function: returns a ranking with value at rank 0.
(define !
  (lambda (value)
    (mark-as-rf
     (element (delay value) 0 terminate-promise))))

;; nrm/exc : macro
;; Usage: (nrm/exc v1 v2 [rank])
;; Constructs a ranking with v1 at rank 0 and v2 at given rank (default 1).
(define-syntax nrm/exc
  (syntax-rules (nrm exc)
    ((nrm/exc r-exp1 r-exp2) (nrm/exc r-exp1 r-exp2 1))
    ((nrm/exc r-exp1 r-exp2 rank)
     (begin
       (unless (rank? rank) (raise-argument-error 'nrm/exc "rank (non-negative integer or infinity)" 1 r-exp1 rank r-exp2))
       (mark-as-rf
        (dedup
         (normalise
          (merge
           (delay (autocast r-exp1))
           (shift rank (delay (autocast r-exp2)))))))))))

;; -----------------------------------------------------------------------------
;; Choice and Observation
;; -----------------------------------------------------------------------------
;; either-of : (Listof Any) -> ranking
(define (either-of lst)
  (unless (list? lst) (raise-argument-error 'either-of "list" 0 lst))
  (letrec
      ((either-of*
        (λ (list)
          (if (empty? list)
              terminate-promise
              (delay (element (delay (car list)) 0 (either-of* (cdr list))))))))
    (mark-as-rf (dedup (either-of* lst)))))

;; either/or : macro
;; Usage: (either/or v ...)
(define-syntax either/or
  (syntax-rules ()
    ((either/or) (mark-as-rf terminate-promise))
    ((either/or r-exp rest ...) (mark-as-rf (dedup (merge (delay (autocast r-exp)) (either* rest ...)))))))

(define-syntax either*
  (syntax-rules ()
    ((either*) terminate-promise)
    ((either* r-exp rest ...) (merge (delay (autocast r-exp)) (either* rest ...)))))

;; observe : (Any -> Boolean) ranking -> ranking
(define (observe pred r)
  (begin
    (unless (one-arg-proc? pred) (raise-argument-error 'observe "predicate" 0 pred r))
    (mark-as-rf (normalise (filter-ranking pred (delay (autocast r)))))))

;; observe-r : Rank (Any -> Boolean) ranking -> ranking
(define (observe-r x pred r) 
  (unless (one-arg-proc? pred) (raise-argument-error 'observe-r "predicate" 0 pred x r))
  (unless (rank? x) (raise-argument-error 'observe-r "rank (non-negative integer or infinity)" 1 pred x r))
  (nrm/exc
   (observe pred r) 
   (observe (compose not pred) r) x))

;; observe-e : Rank (Any -> Boolean) ranking -> ranking
(define (observe-e x pred r)
  (unless (one-arg-proc? pred) (raise-argument-error 'observe-e "predicate" 0 pred x r))
  (unless (rank? x) (raise-argument-error 'observe-e "rank (non-negative integer or infinity)" 1 pred x r))
  (let* ((rp (rank-of pred r)))
    (if (< x rp)
       (observe-r (- rp x) pred r)
       (observe-r (+ (- x rp) (rank-of (compose not pred) r)) pred r))))

;; -----------------------------------------------------------------------------
;; Ranking Manipulation
;; -----------------------------------------------------------------------------
;; cut : Rank ranking -> ranking
(define (cut rank r-exp)
  (unless (rank? rank) (raise-argument-error 'cut "rank (non-negative integer or infinity)" 0 rank r-exp))
  (mark-as-rf (up-to-rank rank (delay (autocast r-exp)))))

;; limit : Nat ranking -> ranking
(define (limit count r-exp)
  (unless (or (exact-nonnegative-integer? count) (infinite? count)) (raise-argument-error 'cut "non-negative integer" 0 rank r-exp))
  (mark-as-rf (filter-after count (delay (autocast r-exp)))))

;; rank-of : (Any -> Boolean) ranking -> Rank
(define (rank-of pred r-exp)
  (unless (one-arg-proc? pred) (raise-argument-error 'rank-of "predicate" 0 pred r-exp))
  (letrec ((rank-of*
            (λ (rf)
              (let* ((res (force rf)))
                (if (infinite? (rank res))
                    (rank res)
                    (if (pred (value res))
                        (rank res)
                        (rank-of* (successor-promise res))))))))
    (rank-of* (delay (autocast r-exp)))))

;; $ : (Function | ranking Function | ranking ...) -> ranking
;; Ranked application: applies function(s) to argument rankings.
(define ($ . r-exps)
  (if (> (length r-exps) 0)
      (if (ranking? (car r-exps))
          ; function argument is ranking over functions
          (mark-as-rf
           (dedup
            (merge-apply
             (map-value
              (λ (form) (delay (autocast (apply (car form) (cdr form)))))
              (dedup (join-list (map (λ (x) (delay (autocast x))) r-exps))))
             (λ (rf) rf))))
          (if (primitive? (car r-exps))
              ; function argument is primitive (function will not return ranking)
              (mark-as-rf
               (dedup
                (map-value
                 (λ (args) (apply (car r-exps) args))
                 (dedup (join-list (map (λ (x) (delay (autocast x))) (cdr r-exps)))))))
              ; function argument is not primitive (function may return ranking)
              (mark-as-rf
               (dedup
                (merge-apply
                 (map-value
                  (λ (args) (delay (autocast (apply (car r-exps) args))))
                  (dedup (join-list (map (λ (x) (delay (autocast x))) (cdr r-exps)))))
                 (λ (rf) rf))))))
      (raise-arity-error '$ (arity-at-least 1))))

;; -----------------------------------------------------------------------------
;; Ranked Let Macros
;; -----------------------------------------------------------------------------
;; rlet : macro
;; Usage: (rlet ((var expr) ...) body ...)
(define-syntax rlet
  (syntax-rules ()
    ((rlet ((var r-exp) ...) body ...)
      ($ (λ (var ...) body ...) r-exp ...))))

;; rlet* : macro
;; Usage: (rlet* ((var expr) ...) body ...)
(define-syntax rlet*
  (syntax-rules ()
    ((rlet* () body) body) ; base case
    ((rlet* ((var r-exp) rest ...) body) ; binding case
      ($ (λ (var) (rlet* (rest ...) body)) r-exp))))

;; -----------------------------------------------------------------------------
;; Ranking Equality and Conversion
;; -----------------------------------------------------------------------------
;; rf-equal? : (ranking ranking) -> Boolean
(define (rf-equal? r-exp1 r-exp2)
  (equal? (rf->hash r-exp1) (rf->hash r-exp2)))

;; rf->hash : (ranking) -> HashTable
(define (rf->hash r-exp)
  (convert-to-hash (delay (autocast r-exp))))
  
;; rf->assoc : (ranking) -> (Listof (Pair Any Rank))
(define (rf->assoc r-exp)
  (convert-to-assoc (dedup (delay (autocast r-exp)))))

;; rf->stream : (ranking) -> Stream
(define (rf->stream r-exp)
  (convert-to-stream (dedup (delay (autocast r-exp)))))

;; -----------------------------------------------------------------------------
;; Display Utilities
;; -----------------------------------------------------------------------------
;; Display helper functions
(define display-header (λ () (begin (display "Rank  Value") (newline) (display "------------") (newline))))
(define display-failure (λ () (begin (display "Failure (empty ranking)") (newline))))
(define display-done (λ () (begin (display "Done") (newline))))
(define display-more (λ () (begin (display "...") (newline))))
(define display-element (λ (el) (begin (display (~a (rank el) #:min-width 5)) (display " ") (display (value el)) (newline))))

;; pr-all : (ranking) -> Void
(define (pr-all r-exp)
  (unless (void? r-exp)
    (let ((first-res (force (autocast r-exp))))
      (if (infinite? (rank first-res))
          (display-failure)
          (begin (display-header) (do-with (delay first-res) display-element) (display-done))))))

;; pr-until : (Rank ranking) -> Void
(define (pr-until r r-exp)
  (unless (rank? r) (raise-argument-error 'observe-j "rank (non-negative integer or infinity)" 0 rank r-exp))
  (unless (void? r-exp)
    (let ((first-res (force (autocast r-exp))))
      (if (infinite? (rank first-res))
          (display-failure)
          (begin (display-header) (pr-until* r first-res))))))

(define (pr-until* r res)
  (if (infinite? (rank res))
      (display-done)
      (if (> (rank res) r)
          (display-more)
          (begin (display-element res) (pr-until* r (successor res))))))

;; pr-first : (Nat ranking) -> Void
(define (pr-first n r-exp)
  (unless (void? r-exp)
    (let ((first-res (force (autocast r-exp))))
      (if (infinite? (rank first-res))
          (display-failure)
          (begin (display-header) (pr-first* n first-res))))))

(define (pr-first* n res)
  (if (infinite? (rank res))
          (display-done)
          (begin (display-element res)
                 (if (= n 1) (display-more) (pr-first* (- n 1) (successor res))))))

;; pr : (ranking) -> Void
(define (pr r-exp) (pr-first 10 r-exp))

;; -----------------------------------------------------------------------------
;; Global Deduplication Setting
;; -----------------------------------------------------------------------------
;; set-global-dedup : Boolean -> Void
(define (set-global-dedup x) (set-core-global-dedup x))

;; =============================================================================
;; End of Ranked Programming API Layer
;; =============================================================================


