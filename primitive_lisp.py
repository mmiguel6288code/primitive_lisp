"""
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
"""
import re, traceback, pdb, sys, readline, logarhythm

logger = logarhythm.get_logger()
logger.level = logarhythm.INFO
auto_debug = True

class Lisp():
    def __init__(self,variables=None):
        self.evaluator = Evaluator(variables)
        self('''
(defun subst (x y z)
    (cond ((atom z)
        (cond ((eq z y) x)
            ('#t z)))
        ('#t (cons (subst x y (car z))
            (subst x y (cdr z))))))
(defun null (x)
    (eq x '()))

(defun and (x y)
    (cond (x (cond (y '#t) ('#t '#f)))
        ('#t '#f)))

(defun or (x y)
    (cond ((not x) (cond ((not y) '#f) ('#t '#t))) ('#t '#t)))

(defun not (x)
    (cond (x '#f) ('#t '#t)))

(defun concat (x y)
    (cond ((null x) y)
        ('#t (cons (car x) (concat (cdr x) y)))))

(defun zip (x y)
    (cond ( (and (null x) (null y)) '())
        ( (and (not (atom x)) (not (atom y)))
            (cons (list (car x) (car y))
                (zip (cdr x) (cdr y))))))

(defun assoc (x y)
    (cond 
        ((atom y) x)
        ((eq (caar y) x) (cadar y))
        ('#t (assoc x (cdr y)))))

(defun eval (e a)
    (cond
        ((atom e) (assoc e a)) ; if an atom, check the environment
        ((atom (car e))
            (cond
                ((eq (car e) 'quote) (cadr e))
                ((eq (car e) 'atom) (atom (eval (cadr e) a)))
                ((eq (car e) 'eq) (eq (eval (cadr e) a)
                                    (eval (caddr e) a)))
                ((eq (car e) 'car) (car (eval (cadr e) a)))
                ((eq (car e) 'cdr) (cdr (eval (cadr e) a)))
                ((eq (car e) 'cons) (cons (eval (cadr e) a)
                                        (eval (caddr e) a)))
                ((eq (car e) 'cond) (evcon (cdr e) a))
                ('#t (eval (cons (assoc (car e) a)
                                    (cdr e))
                            a))))
            ((eq (caar e) 'label)
                (eval (cons (caddar e) (cdr e))
                    (cons (list (cadar e) (car e)) a)))
            ((eq (caar e) 'lambda)
                (eval (caddar e)
                    (concat (zip (cadar e) (evlis (cdr e) a))
                        a)))))
(defun evcon (c a)
    (cond ((eval (caar c) a)
        (eval (cadar c) a))
        ('#t (evcon (cdr c) a))))

(defun evlis (m a)
    (cond ((null m) '())
        ('#t (cons (eval (car m) a)
            (evlis (cdr m) a)))))
               ''')

    def __call__(self,expr):
        return Expression(expr)(self.evaluator)

    def repl(self):
        while True:
            try:
                parsed = Expression(input('lisp> '))
                while not parsed.complete:
                    parsed.resume(input('...> '))
                logger.debug(f'Parse expression: {repr(parsed)}')
                value = parsed(self.evaluator)
                print('=',value)
            except KeyboardInterrupt:
                break
            except:
                e,v,t = sys.exc_info()
                traceback.print_exception(e,v,t)
                if auto_debug:
                    pdb.post_mortem(t)

class Expression():
    def __init__(self,expr,parent=None,**kwargs):
        self.subexpressions = []
        self.consumed_chars = 0
        self.complete = False
        self.parent = parent
        self.current_child = None
        self.expr = expr
        self.__dict__.update(kwargs)
        self.parse(expr)
        self.expr = expr[:self.consumed_chars]
    def resume(self,expr):
        original_length = self.consumed_chars
        self.parse(expr,resume=True)
        self.expr += expr[:self.consumed_chars-original_length]
    def parse_start_trace(self):
        if logger.level > logarhythm.DEBUG:
            return
        ancestry = [self]
        parent = self.parent
        while parent is not None:
            ancestry.insert(0,parent)
            parent = parent.parent
        indent = ' '*4
        lines = ['','Parse Start Trace:']
        for i,parsed in enumerate(ancestry,1):
            lines.append(indent*i+repr(parsed))
        logger.debug('\n'.join(lines))

    def parse_end_trace(self):
        if logger.level > logarhythm.DEBUG:
            return
        ancestry = [self]
        parent = self.parent
        while parent is not None:
            ancestry.insert(0,parent)
            parent = parent.parent
        indent = ' '*4
        lines = ['','Parse End Trace:',indent+repr(self)]
        indent_level = 1
        self._parse_end_trace(indent,indent_level,lines)
        logger.debug('\n'.join(lines))

    def _parse_end_trace(self,indent,indent_level,lines):
        for parsed in self.subexpressions:
            lines.append(indent*(indent_level+1)+repr(parsed))
            parsed._parse_end_trace(indent,indent_level+1,lines)
        if not self.complete:
            lines.append(indent*(indent_level+1)+'...')

    def parse(self,expr,single=False,resume=False):
        self.parse_start_trace()
        while len(expr) > 0:
            #remove leading whitespace
            new_expr = expr.lstrip()
            self.consumed_chars += len(expr) - len(new_expr)
            expr = new_expr
            if len(expr) == 0:
                break

            if expr[0] == '(' or (resume and isinstance(self.current_child,List)):
                if not resume or self.current_child is None:
                    self.current_child = List(expr,self)
                else:
                    self.current_child.resume(expr)
                expr = self.consume(self.current_child,expr)
            elif expr[0] == "'" or (resume and isinstance(self.current_child,Quote)):
                if not resume or self.current_child is None:
                    self.current_child = Quote(expr)
                else:
                    self.current_child.resume(expr)
                expr = self.consume(self.current_child,expr)
            elif expr[0] == ')':
                expr = self.close(expr)
                break
            elif expr[0] == ';':
                #comment
                m = re.match(';.+?\n',expr)
                self.consumed_chars += len(m.group(0))
                expr = expr[m.end(0):]
                continue
            else:
                if resume and (type(self) is Expression or isinstance(self,List)):
                    if len(self.subexpressions) > 0 and isinstance(self.subexpressions[-1],Atom):
                        if not self.expr.endswith(' '):
                            self.expr += ' '
                            self.consumed_chars += 1
                            parent = self.parent
                            while parent is not None:
                                parent.expr += ' '
                                parent.consumed_chars += 1
                                parent = parent.parent

                self.current_child = Atom(expr)
                expr = self.consume(self.current_child,expr)
            if single:
                expr = self.close(expr)
                break
        if type(self) is Expression and self.current_child is None:
            expr = self.close(expr)
        self.parse_end_trace()
        return expr

    def consume(self,subexpression,expr):
        if not (len(self.subexpressions) > 0 and self.current_child is self.subexpressions[-1]):
            self.subexpressions.append(subexpression)
            self.consumed_chars += subexpression.consumed_chars
        if self.current_child.complete:
            self.current_child = None
        return expr[subexpression.consumed_chars:]

    def close(self,expr):
        self.complete = True
        return expr

    def __repr__(self):
        if self.complete:
            return f'{type(self).__name__}({repr(self.expr[:self.consumed_chars])})'
        else:
            return f'{type(self).__name__}({repr(self.expr[:self.consumed_chars])},complete=False)'
    def __call__(self,evaluator=None,quoted=False,local_variables=None):
        if quoted:
            results = list(self.subexpressions)
        else:
            results = []
            for subexpression in self.subexpressions:
                results.append(subexpression(evaluator,quoted,local_variables))
        return results
    def is_atomic(self):
        return len(self.subexpressions) == 0

class Atom(Expression):
    def __init__(self,expr,parent=None,**kwargs):
        self.expr = re.match("[^(') \t\n\r;]+",expr).group(0)
        self.consumed_chars = len(self.expr)
        self.current_child = None
        self.parent = parent
        self.complete = True
        self.__dict__.update(kwargs)
    def resume(self,expr,parent=None):
        raise Exception('Not valid to resume on an atom')

    def __call__(self,evaluator=None,quoted=False,local_variables=None):
        if quoted:
            return self
        elif local_variables is not None and self.expr in local_variables:
            return local_variables[self.expr]

        else:
            return evaluator[self.expr]

    def _parse_end_trace(self,indent,indent_level,lines):
        return
    def is_atomic(self):
        return True
    def __eq__(self,other):
        return isinstance(other,Atom) and self.expr == other.expr


class Quote(Expression):
    def __init__(self,expr,parent=None,**kwargs):
        self.subexpression = None
        self.consumed_chars = 1
        self.parent = parent
        self.current_child = None
        self.complete = False
        self.expr = expr
        self.__dict__.update(kwargs)
        self.parse(expr[1:],single=True)
        self.expr = expr[:self.consumed_chars]
    def consume(self,subexpression,expr):
        self.subexpression = subexpression
        self.consumed_chars += subexpression.consumed_chars
        if self.current_child.complete:
            self.current_child = None
        return expr[subexpression.consumed_chars:]
    def __call__(self,evaluator=None,quoted=True,local_variables=None):
        return self.subexpression(evaluator,quoted=True,local_variables=local_variables)
    def _parse_end_trace(self,indent,indent_level,lines):
        if self.complete:
            parsed = self.subexpression
            lines.append(indent*(indent_level+1)+repr(parsed))
            parsed._parse_end_trace(indent,indent_level+1,lines)
        else:
            lines.append(indent*(indent_level+1)+'...')
    def is_atomic(self):
        return self.subexpression.is_atomic()
    def close(self,expr):
        self.complete = True
        return expr
    def as_list(self):
        if self.complete:
            return List(f'(quote {self.subexpression.expr})')
        else:
            return List('(quote')
    def cdr(self):
        return self.as_list().cdr()

           

    def __eq__(self,other):
        if isinstance(other,Quote) and self.subexpression == other.subexpression:
            return True
        elif isinstance(other,List) and other  == self.as_list():
            return True
        return False


class List(Expression):
    def __init__(self,expr=None,parent=None,**kwargs):
        self.subexpressions = []
        self.consumed_chars = 1
        self.parent = parent
        self.current_child = None
        self.complete = False
        self.expr = expr
        self.__dict__.update(kwargs)
        self.parse(expr[1:])
        self.expr = expr[:self.consumed_chars]
    def close(self,expr):
        self.consumed_chars += 1
        self.complete = True
        return expr[1:]
    def consume(self,subexpression,expr):
        self.subexpressions.append(subexpression)
        self.consumed_chars += subexpression.consumed_chars
        if self.current_child.complete:
            self.current_child = None
        return expr[subexpression.consumed_chars:]
    def __iter__(self):
        yield from self.subexpressions
    def __call__(self,evaluator=None,quoted=False,local_variables=None):
        if quoted:
            return self
        else:
            return evaluator(self,local_variables)
    def _parse_end_trace(self,indent,indent_level,lines):
        for parsed in self.subexpressions:
            lines.append(indent*(indent_level+1)+repr(parsed))
            parsed._parse_end_trace(indent,indent_level+1,lines)
        if not self.complete:
            lines.append(indent*(indent_level+1)+'...')
    def is_atomic(self):
        return len(self.subexpressions) == 0
    def __eq__(self,other):
        if isinstance(other,List) and self.subexpressions == other.subexpressions:
            return True
        elif isinstance(other,Quote) and self.subexpressions == other.as_list().subexpressions:
            return True
        return False
    def cdr(self):
        return List('('+' '.join([x.expr for x in self.subexpressions[1:]])+')')
    def cons(self,new_car):
        return List('('+new_car.expr+' '+' '.join([x.expr for x in self.subexpressions])+')')

class Function(List):
    
    def __init__(self,arg_expr_list,body,parsed_list,scoped_variables=None):
        self.__dict__.update(parsed_list.__dict__)
        self.arg_expr_list = arg_expr_list
        self.body = body
        self.scoped_variables = scoped_variables
        if self.parent.current_child is parsed_list:
            self.parent.current_child = self
    def __call__(self,evaluator=None,quote=False,local_variables=None):
        raise Exception('Functions don\'t have a direct value')

class Evaluator():
    constants = {
        '#t':Atom('#t'),
        '#f':Atom('#f'),
            }
    def __init__(self,variables=None):
        if variables is None:
            variables = {}
        self.variables = variables
        self.variables.update(self.constants)
    def __getitem__(self,variable_name):
        try:
            return int(variable_name)
        except:
            pass
        try:
            return float(variable_name)
        except:
            pass
        if variable_name.startswith('"'):
            try:
                return eval(variable_name)
            except:
                pass
        if variable_name in self.variables:
            return self.variables[variable_name]
        else:
            raise Exception(f'Unbound variable: {variable_name}')
    def __setitem__(self,variable_name,value):
        if not isinstance(value,Expression):
            raise Exception('Variables must map to expressions')
        else:
            self.variables[variable_name] = value
    def trace(self,parsed_list,local_variables):
        if logger.level > logarhythm.DEBUG+5:
            return
        logger.log(logarhythm.DEBUG+5,'Eval trace: ' + repr(parsed_list))


    def __call__(self,parsed_list,local_variables=None):
        """
        Variable scoping:
            global: Evaluator.variables
            function scoped: specific to function, present in all calls to that function
            local scoped: the argument substitutions when calling a function
        """
        self.trace(parsed_list,local_variables)

        subexpressions = parsed_list
        operator,*args = subexpressions
        if isinstance(operator,Atom):
            operator_name = operator.expr
            method_name = f'op_{operator_name}'
            if hasattr(self,method_name):
                return getattr(self,method_name)(parsed_list,local_variables,*args)
            else:
                if local_variables is not None and operator_name in local_variables:
                    operator = local_variables[operator_name]
                else:
                    if operator_name in self.variables:
                        operator = self.variables[operator_name]
                    else:
                        if re.search('^c[ad]{2,4}r$',operator_name) is not None:
                            if len(args) != 1:
                                raise Exception("car/cdr variants require a single list argument")
                            result = args[0](self,local_variables=local_variables)
                            for charac in operator_name[-2:0:-1]:
                                if charac == 'a':
                                    result = result.subexpressions[0]
                                elif charac == 'd':
                                    result = result.cdr()
                                else:
                                    assert (False)
                            return result
                            
                        else:
                            raise Exception('Unbounded variable name: %s' % operator_name)
                    
        if isinstance(operator,List):
            if not isinstance(operator,Function):
                operator = operator(self,local_variables=local_variables)
            if isinstance(operator,Function):
                if local_variables is None:
                    function_variables = {}
                else:
                    function_variables = dict(local_variables)
                if operator.scoped_variables is not None:
                    function_variables.update(operator.scoped_variables)
                apply_values = []
                for apply_arg in args:
                    apply_value = apply_arg(self,local_variables=local_variables)
                    apply_values.append(apply_value)
                function_variables.update(dict(zip(operator.arg_expr_list,apply_values)))
                return operator.body(self,local_variables=function_variables)
            else:
                pdb.set_trace()
        else:
            pdb.set_trace()

    def op_quote(self,parsed_list,local_variables,arg):
        return arg
    def op_atom(self,parsed_list,local_variables,arg):
        value = arg(self,local_variables=local_variables)
        if value.is_atomic():
            return self['#t']
        else:
            return self['#f']
    def op_eq(self,parsed_list,local_variables,arg1,arg2):
        value1 = arg1(self,local_variables=local_variables)
        value2 = arg2(self,local_variables=local_variables)
        if value1 == value2:
            return self['#t']
        else:
            return self['#f']
    def op_car(self,parsed_list,local_variables,arg):
        value = arg(self,local_variables=local_variables)
        if isinstance(value,Quote):
            value = value.as_list()
        if not isinstance(value,List):
            raise Exception('car arg must be list')
        return value.subexpressions[0]

    def op_cdr(self,parsed_list,local_variables,arg):
        value = arg(self,local_variables=local_variables)
        if isinstance(value,Quote):
            value = value.as_list()
        if not isinstance(value,List):
            raise Exception('cdr arg must be list')
        return value.cdr()

    def op_cons(self,parsed_list,local_variables,arg1,arg2):
        value1 = arg1(self,local_variables=local_variables)
        value2 = arg2(self,local_variables=local_variables)
        if isinstance(value2,Quote):
            value2 = value2.as_list()
        if not isinstance(value2,List):
            raise Exception('cons second arg must be list')
        return value2.cons(value1)
    def op_cond(self,parsed_list,local_variables,*args):
        for p,e in args:
            pval = p(self,local_variables=local_variables)
            if pval != self['#f']:
                return e(self,local_variables=local_variables)
        return List('()')
    def op_lambda(self,parsed_list,local_variables,arglist, body):
        arg_expr_list = []
        for arg in arglist:
            if not isinstance(arg,Atom):
                raise Exception('Function arguments must be Atoms')
            arg_expr_list.append(arg.expr)
        return Function(arg_expr_list,body,parsed_list)
    def op_label(self,parsed_list,local_variables,func_name,func_list):
        func = func_list(self,local_variables=local_variables)
        label_func = Function(func.arg_expr_list,func.body,parsed_list)
        if label_func.scoped_variables is None:
            label_func.scoped_variables = {}
        label_func.scoped_variables[func_name.expr] = label_func
        return label_func

    def op_defun(self,parsed_list,local_variables,func_name,arglist,body):
        arg_expr_list = []
        for arg in arglist:
            if not isinstance(arg,Atom):
                raise Exception('Function arguments must be Atoms')
            arg_expr_list.append(arg.expr)
        func = Function(arg_expr_list,body,parsed_list)
        if func.scoped_variables is None:
            func.scoped_variables = {}
        func.scoped_variables[func_name.expr] = func
        self.variables[func_name.expr] = func
        return func
    def op_setq(self,parsed_list,local_variables,variable_name,parsed_value):
        value = parsed_value(self,local_variables=local_variables)
        self.variables[variable_name.expr] = value
        return value
    def op_list(self,parsed_list,local_variables,*args):
        return List(f'({" ".join([arg(self,local_variables=local_variables).expr for arg in args])})')


if __name__ == '__main__':
    import os
    os.environ['PYTHONINSPECT'] = '1'
    #e = Expression('(quote a)')
    Lisp().repl()
