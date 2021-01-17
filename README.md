# primitive_lisp

Goal is to develop the minimal lisp (with minor differences) to Paul Graham's Root of Lisp paper.
http://www.paulgraham.com/rootsoflisp.html


I created this in order to learn more about Lisp.
This simple interpreter implements all the examples in the paper:
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

To do:
- Clean up variable scope ideas. Lexical scoping seems to be the preferred way.
- Allow writing a python function using lisp: function inputs show up in the lisp scope, make callable like any other function
- Macros
- 
