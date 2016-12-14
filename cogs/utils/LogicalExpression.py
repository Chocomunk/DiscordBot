import collections
import copy

class MismatchedParentheses(Exception):
    def __init__(self, expr):
        Exception.__init__(self, 'Mismatched parentheses in Logical Expression: {}'.format(expr))
class IncompleteExpression(Exception):
    def __init__(self, expr):
        Exception.__init__(self, 'Logical Sentence not complete: {}'.format(expr))

class deque(collections.deque):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def peek(self):
        ret = self.pop()
        self.append(ret)
        return copy.deepcopy(ret)

    def peekleft(self):
        ret = self.popleft()
        self.appendleft(ret)
        return copy.deepcopy(ret)

operators = {'!' : 0,
             '&' : 1,
             '|' : 2
             }

class LogicalExpression:

    def __init__(self, expression):
        self.expr = expression
        self.vars = []
        self.RPN = self.infix2RPN(self.expr)
        self.regex = self.RPN2Regex(self.RPN)

    def isHigherPrecedence(self, op1, op2):
        return operators[op1] >= operators[op2]

    def infix2RPN(self, expr):
        output = ''
        stack = deque()

        openP = 0; closedP = 0

        for s in expr.split():
            if s in operators:
                while stack and self.isHigherPrecedence(s, stack.peek()):
                    output += stack.pop() + ' '
                stack.append(s)
            elif s is '(':
                stack.append(s)
                openP+=1
            elif s is ')':
                closedP+=1

                while stack.peek() is not '(':
                    if not stack:
                        raise MismatchedParentheses(self.expr)
                    output += stack.pop() + ' '
                stack.pop()
            else:
                output += s + ' '
                if s not in self.vars:
                    self.vars.append(s)

        while stack:
            output += stack.pop() + ' '
        if openP != closedP:
            raise MismatchedParentheses(self.expr)

        return output

    def RPN2Regex(self, expr):
        stack = deque()

        for s in expr.split():
            if s not in operators:
                if s:
                    stack.append(s)
            else:
                a = ''
                if stack:
                    a = stack.pop()
                else:
                    raise IncompleteExpression(self.expr)

                if s is '!':
                    stack.append('!'+a)
                else:
                    b = ''
                    if stack:
                        b = stack.pop()
                    else:
                        raise IncompleteExpression(self.expr)

                    if '!' in a:
                        p1 = '(?!.*({}))'.format(a[1:])
                    else:
                        p1 = '(?=.*({}))'.format(a)
                    if '!' in b:
                        p2 = '(?!.*({}))'.format(b[1:])
                    else:
                        p2 = '(?=.*({}))'.format(b)

                    if s is '&':
                        stack.append('({0}{1})'.format(p1,p2))
                    elif s is '|':
                        # stack.append('(?=.*({0}|{1}))'.format(p1,p2))
                        stack.append('({0}|{1})'.format(p1,p2))
        return r'(?=.*({0}))'.format(stack.pop())
