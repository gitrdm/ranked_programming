#lang racket

;(require "main.rkt")
(require "rp-api.rkt")
(require "rp-core.rkt")

(module+ test
  
  (require rackunit)
  
  ; rf-equal as check
  (define-simple-check (check-rf-equal? r-exp1 r-exp2)
    (rf-equal? r-exp1 r-exp2))
  
  (test-case
   "nrm/exc"
   (check-rf-equal? (nrm/exc 1 2 1)
                    (construct-ranking (1 . 0) (2 . 1)))
   (check-rf-equal? (nrm/exc 1 2 2)
                    (construct-ranking (1 . 0) (2 . 2)))
   (check-rf-equal? (nrm/exc 1 1 1)
                    (construct-ranking (1 . 0)))
   (check-rf-equal? (nrm/exc 1 (nrm/exc 2 3 1) 1)
                    (construct-ranking (1 . 0) (2 . 1) (3 . 2)))
   (check-rf-equal? (nrm/exc (nrm/exc 10 20 5) 2 1)
                    (construct-ranking (10 . 0) (2 . 1) (20 . 5))))
  
  (test-case
   "either-of"
   (check-rf-equal? (either-of (list 1 2 3))
                    (construct-ranking (1 . 0) (2 . 0) (3 . 0)))
   (check-rf-equal? (either-of `())
                    (failure)))
  
  (test-case
   "either/or test"
   (check-rf-equal? (either/or)
                    (failure))
   (check-rf-equal? (either/or 1)
                    (construct-ranking (1 . 0)))
   (check-rf-equal? (either/or 1 2)
                    (construct-ranking (1 . 0) (2 . 0)))
   (check-rf-equal? (either/or 1 2 3)
                    (construct-ranking (1 . 0) (2 . 0) (3 . 0)))
   (check-rf-equal? (either/or (nrm/exc 1 2 1) (nrm/exc 10 20 10))
                    (construct-ranking (1 . 0) (10 . 0) (2 . 1) (20 . 10))))
  
  (test-case
   "observe"
   (check-rf-equal? (observe odd? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (1 . 0) (3 . 2)))
   (check-rf-equal? (observe even? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (2 . 2)))
   (check-rf-equal? (observe (lambda (x) #F) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (failure))
   (check-rf-equal? (observe (lambda (x) #T) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))))
  
  (test-case
   "observe-r"
   (check-rf-equal? (observe-r 100 odd? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (1 . 0) (3 . 2) (0 . 100) (2 . 102)))
   (check-rf-equal? (observe-r 100 even? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (2 . 2) (1 . 100) (3 . 102)))
   (check-rf-equal? (observe-r 100 (lambda (x) #F) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
   (check-rf-equal? (observe-r 100 (lambda (x) #T) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))))
  
  (test-case
   "observe-e"
   (check-rf-equal? (observe-e 100 odd? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (1 . 0) (3 . 2) (0 . 99) (2 . 101)))
   (check-rf-equal? (observe-e 100 even? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (2 . 2) (1 . 101) (3 . 103)))
   (check-rf-equal? (observe-e 100 (lambda (x) #F) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (failure))
   (check-rf-equal? (observe-e 100 (lambda (x) #T) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))))
  
  (test-case
   "cut"
   (check-rf-equal? (cut 0 (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0)))
   (check-rf-equal? (cut 1 (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1)))
   (check-rf-equal? (cut 3 (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3)))
                    (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))))
  
  (test-case
   "rank-of"
   (check-equal? (rank-of odd? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))) 1)
   (check-equal? (rank-of even? (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))) 0)
   (check-equal? (rank-of (lambda (x) (> x 2)) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))) 3)
   (check-true (infinite? (rank-of (lambda (x) #F) (construct-ranking (0 . 0) (1 . 1) (2 . 2) (3 . 3))))))
  
  (test-case
   "ranked application"
   (check-rf-equal? ($ + 10 5)
                    (construct-ranking (15 . 0)))
   (check-rf-equal? ($ (nrm/exc + - 1) 10 5)
                    (construct-ranking (15 . 0) (5 . 1)))
   (check-rf-equal? ($ + (nrm/exc 10 20 1) 5)
                    (construct-ranking (15 . 0) (25 . 1)))
   (check-rf-equal? ($ + (nrm/exc 10 20 1) (nrm/exc 5 50 2))
                    (construct-ranking (15 . 0) (25 . 1) (60 . 2) (70 . 3)))
   (check-rf-equal? ($ (nrm/exc + - 1) (nrm/exc 10 20 1) (nrm/exc 5 50 2))
                    (construct-ranking (15 . 0) (25 . 1) (5 . 1) (60 . 2) (15 . 2) (70 . 3) (-40 . 3) (-30 . 4)))
   (check-rf-equal? ($ + (nrm/exc 10 20 1) (nrm/exc 5 (nrm/exc 50 500 2) 2))
                    (construct-ranking (15 . 0) (25 . 1) (60 . 2) (70 . 3) (510 . 4) (520 . 5))))
  
  (test-case
   "rlet"
   (check-rf-equal? (rlet ((x (nrm/exc 1 2 1))) x)
                    (construct-ranking (1 . 0) (2 . 1)))
   (check-rf-equal? (rlet ((x (nrm/exc 1 2 1)) (y (nrm/exc 10 20 2))) (list x y))
                    (construct-ranking ((1 10) . 0) ((2 10) . 1) ((1 20) . 2) ((2 20) . 3)))
   (check-rf-equal? (rlet ((x (nrm/exc 1 2 1)) (y (failure))) (list x y))
                    (failure)))
  
  (test-case
   "rlet*"
   (check-rf-equal? (rlet* ((x (nrm/exc 1 2 1))) x)
                    (construct-ranking (1 . 0) (2 . 1)))
   (check-rf-equal? (rlet* ((x (nrm/exc #F #T 1)) (y (if x (nrm/exc 1 2 1) 0))) (list x y))
                    (construct-ranking ((#F 0) . 0) ((#T 1) . 1) ((#T 2) . 2)))
   (check-rf-equal? (rlet* ((x (nrm/exc 1 2 1)) (y (failure))) (list x y))
                    (failure)))
  
  (test-case
   "rf-equal"
   (check-true (rf-equal? (failure) (failure)))
   (check-true (rf-equal? (construct-ranking (0 . 0)) (construct-ranking (0 . 0))))
   (check-true (rf-equal? (construct-ranking (0 . 0) (1 . 1)) (construct-ranking (0 . 0) (1 . 1))))
   (check-false (rf-equal? (construct-ranking (0 . 0) (1 . 1)) (construct-ranking (0 . 0) (1 . 2))))
   (check-false (rf-equal? (construct-ranking (0 . 0) (1 . 1)) (construct-ranking (0 . 0) (2 . 1))))
   (check-false (rf-equal? (construct-ranking (0 . 0) (1 . 1)) (construct-ranking (0 . 0))))
   (check-false (rf-equal? (construct-ranking (0 . 0)) (construct-ranking (0 . 0) (1 . 1))))
   (check-false (rf-equal? (construct-ranking (0 . 0)) (failure))))
  
  (test-case
   "rf->hash"
   (let ((hash1 (rf->hash (failure)))
         (hash2 (rf->hash (construct-ranking (1 . 0))))
         (hash3 (rf->hash (construct-ranking (1 . 0) (2 . 1))))
         (hash4 (rf->hash (construct-ranking (1 . 0) (2 . 1) (2 . 2)))))
     (check-equal? (hash-count hash1) 0)
     (check-equal? (hash-count hash2) 1)
     (check-equal? (hash-count hash3) 2)
     (check-equal? (hash-count hash4) 2)
     (check-equal? (hash-ref hash2 1) 0)
     (check-equal? (hash-ref hash3 1) 0)
     (check-equal? (hash-ref hash3 2) 1)
     (check-equal? (hash-ref hash4 1) 0)
     (check-equal? (hash-ref hash4 2) 1)))
  
  (test-case
   "rf->assoc"
   (let ((r1 (failure))
         (r2 (construct-ranking (1 . 0)))
         (r3 (construct-ranking (1 . 0) (2 . 1))))
     (check-equal? (rf->assoc (failure)) `())
     (check-equal? (rf->assoc (construct-ranking (1 . 0))) `((1 . 0)))
     (check-equal? (rf->assoc (construct-ranking (1 . 0) (2 . 1))) `((1 . 0) (2 . 1)))
     (check-equal? (rf->assoc (construct-ranking (1 . 0) (2 . 1) (2 . 2))) `((1 . 0) (2 . 1)))))
  
  (test-case
   "set-global-dedup"
   (let ((with_dedup     (begin (set-global-dedup #T) (rf->assoc (nrm/exc 10 10 10))))
         (without-dedup  (begin (set-global-dedup #F) (let ((ret (rf->assoc (nrm/exc 10 10 10)))) (begin (set-global-dedup #T) ret)))))
     (check-equal? with_dedup    `((10 . 0)))
     (check-equal? without-dedup `((10 . 0) (10 . 10)))))
  
  ;; Test: map-value and normalise
  (test-case
   "map-value and normalise"
   (let* ((r (construct-ranking (1 . 2) (2 . 4) (3 . 7)))
          (mapped (map-value (lambda (x) (* x 10)) r))
          (normed (normalise r)))
     (check-equal? (rf->assoc mapped) '((10 . 2) (20 . 4) (30 . 7)))
     (check-equal? (rf->assoc normed) '((1 . 0) (2 . 2) (3 . 5)))))
  
  ;; Test: shift
  (test-case
   "shift"
   (let* ((r (construct-ranking (1 . 0) (2 . 2) (3 . 5)))
          (shifted (shift 10 r)))
     (check-equal? (rf->assoc shifted) '((1 . 10) (2 . 12) (3 . 15)))))
  
  ;; Test: filter-ranking
  (test-case
   "filter-ranking"
   (let* ((r (construct-ranking (1 . 0) (2 . 1) (3 . 2) (4 . 3)))
          (filtered (filter-ranking (lambda (x) (even? x)) r)))
     (check-equal? (rf->assoc filtered) '((2 . 1) (4 . 3)))))
  
  ;; Test: filter-after
  (test-case
   "filter-after"
   (let* ((r (construct-ranking (1 . 0) (2 . 1) (3 . 2) (4 . 3)))
          (filtered (filter-after (lambda (x) (> x 2)) r)))
     (check-equal? (rf->assoc filtered) '((3 . 2) (4 . 3)))))
  
  ;; Test: up-to-rank
  (test-case
   "up-to-rank"
   (let* ((r (construct-ranking (1 . 0) (2 . 1) (3 . 2) (4 . 3)))
          (upto (up-to-rank 2 r)))
     (check-equal? (rf->assoc upto) '((1 . 0) (2 . 1) (3 . 2)))))
  
  ;; Test: dedup
  (test-case
   "dedup"
   (let* ((r (construct-ranking (1 . 0) (1 . 1) (2 . 2) (2 . 3)))
          (deduped (dedup r)))
     (check-equal? (rf->assoc deduped) '((1 . 0) (2 . 2)))))
  
  ;; Test: do-with
  (test-case
   "do-with"
   (let* ((r (construct-ranking (1 . 0) (2 . 1)))
          (result (do-with (lambda (x r) (+ x r)) r)))
     (check-equal? result 3)))
  
  ;; Test: construct-from-assoc
  (test-case
   "construct-from-assoc"
   (let* ((assoc '((a . 0) (b . 1) (c . 2)))
          (r (construct-from-assoc assoc)))
     (check-equal? (rf->assoc r) assoc)))
  
  ;; Test: ! (truth function)
  (test-case
   "! (truth function)"
   (let ((r (! 5)))
     (check-true (ranking? r))
     (check-equal? (rf->assoc r) '((5 . 0)))) )
  
  ;; Test: failure returns empty ranking
  (test-case
   "failure returns empty ranking"
   (let ((r (failure)))
     (check-true (ranking? r))
     (check-equal? (rf->assoc r) '())))
  
  ;; Test: construct-ranking with no arguments returns empty ranking
  (test-case
   "construct-ranking with no arguments returns empty ranking"
   (let ((r (construct-ranking)))
     (check-true (ranking? r))
     (check-equal? (rf->assoc r) '())))
  
  ;; Test: nrm/exc with only one value
  (test-case
   "nrm/exc with one value"
   (let ((r (nrm/exc 42 42 0)))
     (check-true (ranking? r))
     (check-equal? (rf->assoc r) '((42 . 0)))))
  
  ;; Test: cut and limit
  (test-case
   "cut and limit"
   (let ((r (construct-ranking (1 . 0) (2 . 1) (3 . 2) (4 . 3))))
     (check-equal? (rf->assoc (cut 2 r)) '((1 . 0) (2 . 1) (3 . 2)))
     (check-equal? (rf->assoc (limit 2 r)) '((1 . 0) (2 . 1)))) )
  
  ;; Test: pr-all, pr-until, pr-first, pr
  (test-case
   "pr-all, pr-until, pr-first, pr"
   (let ((r (construct-ranking (1 . 0) (2 . 1) (3 . 2))))
     (pr-all r)
     (pr-until 1 r)
     (pr-first 2 r)
     (pr r)))
  
  ;; Test: $ with function returning ranking
  (test-case
   "$ with function returning ranking"
   (let ((r ($ (lambda (x) (nrm/exc x (* x 10) 1)) (nrm/exc 2 3 1))))
     (check-rf-equal? r (construct-ranking (2 . 0) (20 . 1) (3 . 1) (30 . 2)))))

  ;; Test: $ with multiple argument rankings
  (test-case
   "$ with multiple argument rankings"
   (let ((r ($ + (nrm/exc 1 2 1) (nrm/exc 10 20 1))))
     (check-rf-equal? r (construct-ranking (11 . 0) (21 . 1) (12 . 1) (22 . 2)))))

  ;; Test: $ with ranking of functions
  (test-case
   "$ with ranking of functions"
   (let ((r ($ (nrm/exc + - 1) 5 2)))
     (check-rf-equal? r (construct-ranking (7 . 0) (3 . 1)))))

  ;; Test: rlet* with dependency
  (test-case
   "rlet* with dependency"
   (check-rf-equal? (rlet* ((x (nrm/exc 1 2 1)) (y (nrm/exc x 10 1))) (list x y))
                    (construct-ranking ((1 1) . 0) ((2 2) . 1) ((1 10) . 1) ((2 10) . 2))))

  ;; Test: observe with always-false predicate yields failure
  (test-case
   "observe with always-false predicate yields failure"
   (check-rf-equal? (observe (lambda (x) #f) (nrm/exc 1 2 1)) (failure)))

  ;; Test: observe with always-true predicate yields original ranking
  (test-case
   "observe with always-true predicate yields original ranking"
   (let ((r (nrm/exc 1 2 1)))
     (check-rf-equal? (observe (lambda (x) #t) r) (normalise r))))

  ;; Test: observe-e and observe-r with edge cases
  (test-case
   "observe-e and observe-r with edge cases"
   (let ((r (nrm/exc 1 2 1)))
     (check-rf-equal? (observe-e 0 (lambda (x) (= x 1)) r) (construct-ranking (1 . 0) (2 . 1)))
     (check-rf-equal? (observe-r 0 (lambda (x) (= x 2)) r) (construct-ranking (2 . 0) (1 . 1)))))

  ;; Test: cut and limit with empty ranking
  (test-case
   "cut and limit with empty ranking"
   (let ((r (failure)))
     (check-rf-equal? (cut 2 r) (failure))
     (check-rf-equal? (limit 2 r) (failure))))

  ; Add more tests below this line
  
  ) ; This is a closing parenthesis for the module+ test block, so leave it as is



