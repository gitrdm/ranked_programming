#lang racket
(require "../rp-core.rkt")
(require "../rp-api.rkt")

; the hidden markov model example from the paper

; A simple toy-example of a ranking-based hidden markov model specified through
; the parameters init, trans and emit.
(define (init)
  (either/or "rainy" "sunny"))
(define (trans s)
  (case s
    (("rainy") (nrm/exc "rainy" "sunny" 2))
    (("sunny") (nrm/exc "sunny" "rainy" 2))))
(define (emit s)
  (case s
    (("rainy") (nrm/exc "yes" "no" 1))
    (("sunny") (nrm/exc "no" "yes" 1))))

; a generic implementation of a hidden markov model
(define (hmm obs)
  (if (empty? obs)
      ($ list (init))
      ($ cdr
         (observe (lambda (x) (eq? (car x) (car obs)))
                  (rlet* ((p (hmm (cdr obs)))
                          (s (trans (car p)))
                          (o (emit s)))
                         (cons o (cons s p)))))))

; Inference example 1
(pr (hmm `("no" "no" "yes" "no" "no")))

; Inference example 2
(pr (hmm `("yes" "yes" "yes" "no" "no")))

; Utility: force and print the full ranking structure for debugging
(define (force-and-print-ranking rf)
  (let loop ((r (force rf)) (i 0))
    (cond
      [(infinite? (rank r)) (printf "END\n")]
      [else
       (printf "Ranked[~a]: value=~a rank=~a\n" i (value r) (rank r))
       (loop (successor-promise r) (add1 i))])))

(module+ test
  (require rackunit)
  ; Minimal test: check init produces expected ranking
  (define init-ranking (init))
  (define init-list (convert-to-assoc init-ranking))
  (check-true (pair? (car init-list)))
  (force-and-print-ranking init-ranking)
  ; Minimal test: check hmm for 1 observation
  (define hmm1 (hmm '("no")))
  (define hmm1-list (convert-to-assoc hmm1))
  (check-true (pair? (car hmm1-list)))
  (force-and-print-ranking hmm1)
  ; Add more assertions as you refine the structure
)

