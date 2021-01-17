# primitive_lisp

I created this in order to learn more about Lisp.
Goal is to develop the minimal lisp (with minor differences) to Paul Graham's [Root of Lisp paper](http://www.paulgraham.com/rootsoflisp.html). 
The paper is only present in post-script, so I included a pdf version [here](https://raw.githubusercontent.com/mmiguel6288code/primitive_lisp/main/jmc.pdf)

This simple interpreter implements all the examples in the paper.

Operators built into the interpreter:
- quote
- atom
- eq
- car
- cdr
- cons
- cond
- lambda
- label
- defun
- caar/cadr/cdar/cddr/caaar/caadr/.../cddddr
- list

Functions defined from the operators:
- subst
- null
- and
- not
- concat (called append in the paper)
- zip (called pair in the paper)
- assoc
- eval

Functions I added:
- or
- setq

To do:
- Clean up variable scope ideas. Lexical scoping seems to be the preferred way.
- Allow writing a python function using lisp: function inputs show up in the lisp scope, make callable like any other function
- Macros
- Numeric expressions; Operators for math
- String expressions; Operators for strings
- Sets/Dictionaries?


```python
#This calls the lisp object directly. Can alternatively do lisp.repl().
>>> lisp = Lisp()
>>> lisp('''
... (quote a)
... 'a
... (quote (a b c))
... ''')
[Atom('a'), Atom('a'), List('(a b c)')]

>>> lisp('''
... (atom 'a)
... (atom '(a b c))
... (atom '())
... ''')
[Atom('#t'), Atom('#f'), Atom('#t')]

>>> lisp('''
... (atom (atom 'a))
... (atom '(atom 'a))
... ''')
[Atom('#t'), Atom('#f')]

>>> lisp('''
... (eq 'a 'a)
... (eq 'a 'b)
... (eq '() '())
... ''')
[Atom('#t'), Atom('#f'), Atom('#t')]

>>> lisp("(car '(a b c))")
[Atom('a')]

>>> lisp("(cdr '(a b c))")
[List('(b c)')]

>>> lisp('''
... (cons 'a '(b c))
... (cons 'a (cons 'b (cons 'c '())))
... (car (cons 'a '(b c)))
... (cdr (cons 'a '(b c)))
... ''')
[List('(a b c)'), List('(a b c)'), Atom('a'), List('(b c)')]

>>> lisp('''
... (cond ((eq 'a 'b) 'first)
...     ((atom 'a) 'second))
... ''')
[Atom('second')]

>>> lisp('''
... ((lambda (x) (cons x '(b))) 'a)
... ((lambda (x y) (cons x (cdr y)))
...   'z
...   '(a b c))
... ((lambda (f) (f '(b c)))
...   '(lambda (x) (cons 'a x)))
... ''')
[List('(a b)'), List('(z b c)'), List('(a b c)')]

>>> lisp('''
... (subst 'm 'b '(a b (a b c) d))
... ''')
[List('(a m (a m c) d)')]

>>> lisp('''
... (cadr '((a b) (c d) e))
... (caddr '((a b) (c d) e))
... (cdar '((a b) (c d) e))
... (cons 'a ( cons 'b ( cons 'c '())))
... (list 'a 'b 'c)
... ''')
[List('(c d)'), Atom('e'), List('(b)'), List('(a b c)'), List('(a b c)')]

>>> lisp('''
... (null 'a)
... (null '())
... ''')
[Atom('#f'), Atom('#t')]

>>> lisp('''
... (and (atom 'a) (eq 'a 'a))
... (and (atom 'a) (eq 'a 'b))
... ''')
[Atom('#t'), Atom('#f')]

>>> lisp('''
... (not (eq 'a 'a))
... (not (eq 'a 'b))
... ''')
[Atom('#f'), Atom('#t')]

>>> lisp('''
... (concat '(a b) '(c d))
... (concat '() '(c d))
... ''')
[List('(a b c d)'), List('(c d)')]

>>> lisp('''
... (zip '(x y z) '(a b c))
... ''')
[List('((x a) (y b) (z c))')]

>>> lisp('''
... (assoc 'x '((x a) (y b)))
... (assoc 'x '((x new) (x a) (y b)))
... ''')
[Atom('a'), Atom('new')]

>>> lisp('''
... (eval 'x '((x a) (y b)))
... (eval '(eq 'a 'a) '())
... (eval '(cons x '(b c))
...     '((x a) (y b)))
... (eval '(cond ((atom x) 'atom)
...     ('t 'list))
...   '((x '(a b))))
... (eval '(f '(b c))
...    '((f (lambda (x) (cons 'a x)))))
... (eval '((label firstatom (lambda (x)
...     (cond ((atom x) x)
...         ('t (firstatom (car x))))))
...   y)
...  '((y ((a b) (c d)))))
... (eval '((lambda (x y) (cons x (cdr y)))
...     'a
...     '(b c d))
...   '())
... ''')
[Atom('a'), Atom('#t'), List('(a b c)'), Quote("'list"), List("('a b c)"), Atom('a'), List("('a c d)")]
```
