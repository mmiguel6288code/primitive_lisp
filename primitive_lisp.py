import re, traceback, pdb, sys

debug_mode = False
def auto_debug(e,v,t):
    traceback.print_exception(e,v,t)
    pdb.post_mortem(t)
sys.excepthook = auto_debug

def pretty_tokens(tokens):
    s = ' '.join(tokens)
    s = re.sub('\\) ([\')])',')\\1',re.sub('([\'(]) \\(','\\1(',re.sub('\\s*([()\'])\\s*','\\1',s).replace("'"," '").replace('(',' (').replace(')',') ')))
    return s

class LambdaFunction():
    def __init__(self,arguments,expr,tokens):
        self.arguments = arguments
        self.expr = expr
        self.tokens = tokens
    def __str__(self):
        return pretty_tokens(self.tokens)
    def __repr__(self):
        return str(self)

class QuotedAtom():
    def __init__(self,atom):
        self.atom = atom
    def __str__(self):
        return self.atom
    def __repr__(self):
        return str(self)
    def expr(self):
        return "'"+self.atom
    def __eq__(self,other):
        if isinstance(other,QuotedAtom):
            return self.atom == other.atom
        else:
            return self.atom == other
class QuotedList():
    def __init__(self,arguments=None,tokens=None):
        if arguments is None:
            arguments = []
        self.arguments = arguments
        self.tokens=tokens
    def __str__(self):
        #return f'({" ".join([(x.expr() if isinstance(x,QuotedAtom) else str(x)) for x in self])})'
        return f'({" ".join([str(x) for x in self])})'
    def __repr__(self):
        return str(self)
    def expr(self):
        if self.tokens is not None:
            return pretty_tokens(self.tokens)
        return f'({" ".join([str(x) for x in self])})'
    def __iter__(self):
        yield from self.arguments
    def __len__(self):
        return len(self.arguments)
    def __eq__(self,other):
        if isinstance(other,QuotedList):
            return self.arguments == other.arguments
        else:
            return self.arguments == other
           
    def __getitem__(self,index):
        if isinstance(index,slice):
            return QuotedList(self.arguments[index])
        return self.arguments[index]
    def __add__(self,other):
        if isinstance(other,QuotedList):
            return QuotedList(self.arguments + other.arguments)
        else:
            pdb.set_trace()

class State():
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    def eval(self):
        if debug_mode:
            print('-'*80)
            print(f'eval: {self.name}: {str(self)}')
            pdb.set_trace()
        if self.operator == 'quote':
            if len(self.arguments) != 1:
                raise Exception(f'Ill-formed syntax: {str(self)}')
            return self.arguments[0]
        elif self.name == 'list_quote' or self.name == 'lambda_args':
            return QuotedList(self.arguments,self.tokens)
        elif self.name == 'list_cond':
            return self.value
        elif self.name == 'cond_term':
            return self.arguments

        elif self.name == 'list_lambda':
            return LambdaFunction(self.arguments[0],self.arguments[1],self.tokens)

        elif self.operator == 'atom':
            if len(self.arguments) != 1:
                raise Exception(f'Ill-formed syntax: {str(self)}')
            if isinstance(self.arguments[0],QuotedList) and len(self.arguments[0]) > 0:
                return QuotedList()
            else:
                return '#t'
        elif self.operator == 'eq':
            if len(self.arguments) != 2:
                raise Exception(f'Ill-formed syntax: {str(self)}')
            if self.arguments[0] == self.arguments[1]:
                return '#t'
            else:
                return QuotedList()
        elif self.operator == 'car':
            if len(self.arguments) != 1:
                raise Exception(f'Ill-formed syntax: {str(self)}')
            arg = self.arguments[0]
            if not isinstance(arg,QuotedList):
                raise Exception(f'The object {str(arg)}, passed as the first argument to car, is not the correct type.')
            return arg[0]
        elif self.operator == 'cdr':
            if len(self.arguments) != 1:
                raise Exception(f'Ill-formed syntax: {str(self)}')
            arg = self.arguments[0]
            if not isinstance(arg,QuotedList):
                raise Exception(f'The object {str(arg)}, passed as the first argument to car, is not the correct type.')
            return arg[1:]
        elif self.operator == 'cons':
            if len(self.arguments) != 2:
                raise Exception(f'cons has been called with {len(self.arguments)} arguments but requires exactly 2')
            if isinstance(self.arguments[1],QuotedList):
                if isinstance(self.arguments[0],QuotedList):
                    result = self.arguments[0] + self.arguments[1]
                else:
                    result = QuotedList([self.arguments[0]]) + self.arguments[1]
                result.tokens = self.tokens
                return result
            else:
                pdb.set_trace() #dotted pair

        elif isinstance(self.operator,LambdaFunction):
            variables = {arg_name:arg_value for arg_name,arg_value in zip(self.operator.arguments,self.arguments)}

            return lisp(self.operator.expr.expr(),variables)

        else:
            print('Unknown operator: %s' % self.operator)
            pdb.set_trace()

    def __str__(self):
        if self.name == 'top':
            return '<top>'
        return pretty_tokens(self.tokens)
    def __repr__(self):
        return str(self)
    
constants = {'#t':'#t'}
def evaluate_atom(atom,variables):
    try:
        return int(atom)
    except:
        pass
    try:
        return float(atom)
    except:
        pass
    if atom in constants:
        return constants[atom]
    if atom in variables:
        return variables[atom]
    raise Exception('Unbound variable: %s' % atom)


def lisp(expr,variables = None):
    state = State(
            name='top',
            operator=None,
            arguments=[],
            tokens=[],
            )
    stack = []
    if variables is None:
        variables = {}

    while len(expr) > 0:

        expr = expr.lstrip()
        if len(expr) == 0:
            break

        if debug_mode:
            print('-'*80)
            print(f'stack size: {len(stack)}')
            print(f'state.name: {state.name}')
            print(f'state: {str(state)}')
            print(f'state.operator: {str(state.operator)}')
            print(f'state.arguments: {[str(x) for x in state.arguments]}')
            print(f'expr: {expr[:80]}{"..." if len(expr) > 80 else ""}')
            pdb.set_trace()
        if expr[0] == '(':
            stack.append(state)
            if state.operator == 'quote' or state.name == 'list_quote':
                state = State(
                        name='list_quote',
                        operator=None,
                        arguments=[],
                        tokens=['('],
                        )
            elif state.name == 'sugar_quote':
                state = State(
                        name='list_quote',
                        operator=None,
                        arguments=[],
                        tokens=['\'('],
                        )

            elif state.name == 'list_lambda':
                if len(state.arguments) == 0:
                    state = State(
                            name = 'lambda_args',
                            operator = None,
                            arguments = [],
                            tokens = ['('],
                            )
                elif len(state.arguments) == 1:
                    state = State(
                            name='list_quote',
                            operator=None,
                            arguments=[],
                            tokens=['('],
                            )

                else:
                    raise Exception('lambda must have two arguments')
            elif state.name == 'lambda_args':
                raise Exception('lambda variable arguments must be atoms')
            elif state.name == 'list_cond':
                if state.found_term is False:
                    state = State(
                            name='cond_term',
                            operator=None,
                            arguments=[],
                            tokens=['('],
                            )
                else:
                    state = State(
                            name='list_quote',
                            operator=None,
                            arguments=[],
                            tokens=['('],
                            )


            elif state.name == 'cond_term':
                if len(state.arguments) == 0:
                    state = State(
                            name='list_operator',
                            operator=None,
                            arguments=[],
                            tokens=['('],
                            )
                elif len(state.arguments) == 1:
                    if state.arguments[0] == '#t':
                        state = State(
                                name='list_operator',
                                operator=None,
                                arguments=[],
                                tokens=['('],
                                )
                    else:
                        state = State(
                                name='list_quote',
                                operator=None,
                                arguments=[],
                                tokens=['('],
                                )
                else:
                    raise Exception('cond arguments must be pairs')
            else:
                state = State(
                        name='list_operator',
                        operator=None,
                        arguments=[],
                        tokens=['('],
                        )
            expr = expr[1:]
        elif expr[0] == ')':
            state.tokens.append(')')
            value = state.eval()
            lower_tokens = state.tokens
            state = stack.pop()
            state.tokens.extend(lower_tokens)
            if state.name == 'list_operator':
                if isinstance(value,LambdaFunction):
                    state.name = 'list_arguments'
                    state.operator = value
                else:
                    pdb.set_trace()
            else:
                state.arguments.append(value)
                if state.name == 'sugar_quote':
                    lower_tokens = state.tokens
                    state = stack.pop()
                    state.tokens.extend(lower_tokens)
                    state.arguments.append(value)
                elif state.name == 'list_cond':
                    if value[0] == '#t':
                        state.found_term = True
                        state.value = value[1]
            expr = expr[1:]
        elif expr[0] == "'":
            stack.append(state)
            state = State(
                    name='sugar_quote',
                    operator='quote',
                    arguments=[],
                    tokens=["'"],
                    )
            expr = expr[1:]
        else:
            #atom
            m = re.match('[A-Za-z0-9._]+',expr)
            token = m.group(0)
            expr = expr[m.end(0):]
            state.tokens.append(token)

            if state.name == 'list_operator':
                if token in ['quote','atom','eq','car','cdr','cons','cond','lambda']:
                    state.operator = token
                else:
                    value = evaluate_atom(token,variables)
                    #if isinstance(value,QuotedList):
                    #    value = lisp(value.expr(),variables)
                    state.operator = value


                if state.operator == 'quote':
                    state.name = 'list_quote'
                elif state.operator == 'cond':
                    state.name = 'list_cond'
                    state.found_term = False
                    state.value = QuotedList()
                elif state.operator == 'lambda':
                    state.name = 'list_lambda'
                else:
                    state.name = 'list_arguments'

            elif state.name == 'list_arguments':
                if state.operator == 'quote':
                    value = token
                else:
                    value = evaluate_atom(token,variables)
                state.arguments.append(value)
            elif state.name == 'list_quote' or state.name == 'lambda_args':
                value = token
                state.arguments.append(value)
            elif state.name == 'list_cond':
                raise Exception('arguments of cond must be pairs')
            elif state.name == 'list_lambda':
                raise Exception('arguments of lambda must be lists')
            elif state.name == 'cond_term':
                if len(state.arguments) == 0:
                    value = evaluate_atom(token,variables)
                    state.arguments.append(value)
                else:
                    if state.arguments[0] == '#t':
                        value = evaluate_atom(token,variables)
                    else:
                        state.arguments.append(token)
            elif state.name == 'sugar_quote':
                value = QuotedAtom(token)
                state.arguments.append(value)
                lower_tokens = state.tokens
                state = stack.pop()
                state.tokens.extend(lower_tokens)
                state.arguments.append(value)

            elif state.name == 'top':
                atom = token
                value = evaluate_atom(atom,variables)
                return value
            else:
                print('unknown state name: %s' % state.name)
                pdb.set_trace()
    result = state.arguments[0]
    return result

if __name__ == '__main__':
    while True:
        expr = input('> ')
        try:
            result = lisp(expr)
            print('=',str(result))
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
