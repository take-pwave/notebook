import copy
from collections import defaultdict
import time

class Unification():
    empty = None
    def __new__(cls, *args, **kargs):
        if cls.empty == None:
            cls.empty = super(Unification, cls).__new__(cls)
            cls.empty._variables = []
        return super(Unification, cls).__new__(cls)

    def __init__(self, v = None):
        self._variables = []
        if v != None:
            self.addVariable(v)
    
    def addVariable(self, v):
        if not v in self._variables:
            self._variables.append(v)
        return self
    
    def append(self, u):
        for v in u.elements():
            self.addVariable(v)
        return self

    def elements(self):
        return self._variables
    
    def unbind(self):
        for v in self._variables:
            v.unbind()
    
    def __str__(self):
        buf = str()
        for i in range(len(self._variables)):
            if i > 0:
                buf += ", "
            buf += self._variables[i].definitionString()
        return buf
    
class Variable:
    def __init__(self, name):
        self.name = name
        self.instantiation = None
        self.id = name + str(time.time())

    def unify(self, s):
        structureCls = globals()['Structure']
        if isinstance(s, Variable):
            v = s
            if self is v:
                return Unification()
            elif self.instantiation != None:
                return self.instantiation.unify(v)
            elif v.instantiation != None:
                return v.instantiation.unify(self)
            self.instantiation = v
            return Unification(self)
        elif isinstance(s, structureCls):
            if self.instantiation != None:
                return self.instantiation.unify(s)
            self.instantiation = s
            return Unification(self)
        else: # Term
            t = s
            return t.unify(self)
        
    def __eq__(self, o):
        if not isinstance(o, Variable):
            return False
        v = o
        if self.name != v.name:
            return False
        if self.instantiation == None:
            return v.instantiation == None
        return self.instantiation.__eq__(v.instantiation)
    
    def __hash__(self):
        return hash(self.id)
    
    def unbind(self):
        self.instantiation = None

    def eval(self):
        if self.instantiation == None:
            raise Exception("Variable" + self.name + " is undefined")
        return self.instantiation.eval()
    
    def isList(self):
        if self.instantiation != None:
            return self.instantiation.isList()
        return True

    def listTailString(self):
        if self.instantiation != None:
            return self.instantiation.listTailString()
        return f"|{self.name}"
        
    def __str__(self):
        if self.instantiation != None:
            return self.instantiation.__str__()
        return self.name

    def variables(self):
        return Unification(self)
    
    def copyForProof(self, ignored, scope):
        return scope.lookup(self.name)
    
    def definitionString(self):
        if self.instantiation != None:
            return str(self.name) + " = " + str(self.instantiation)
        return self.name

class Structure:
    @classmethod
    def headAndTail(cls, terms, tail):
        if len(terms) == 0:
            raise Exception("Cannot create a list with no head")
        headAndTail = []
        headAndTail.append(terms[0]) 
        if len(terms) == 1:
            headAndTail.append(tail) 
        else:
            rest = copy.copy(terms[1:])
            headAndTail.append(cls.list(rest, tail)) 
        return headAndTail

    @classmethod
    def list(cls, *args):
        factCls = globals()['Fact']
        if len(args) == 1:
            if isinstance(args[0], list):
                terms = args[0]
                emptyListCls = globals()['EmptyList']
                if isinstance(terms[0], Structure) or isinstance(terms[0], Variable):
                    return Structure(".", cls.headAndTail(terms, emptyListCls()))
                else:
                    return Structure(".", cls.headAndTail(factCls.facts(terms), emptyListCls()))
        elif len(args) == 2:
            terms = args[0]
            tail = args[1]
            return Structure(".", cls.headAndTail(terms, tail))
        
    def isList(self):
        return len(self.terms) == 2 and self.functor == "." and self.terms[1].isList()
    
    def listTailString(self):
        return f", {self.listTermsToString()}"
    
    def listTermsToString(self):
        s = self.terms[0].__str__()
        if len(self.terms) > 1:
            s += self.terms[1].listTailString()
        return s
    
    # コンストラクター
    def __init__(self, functor, terms = []):
        self.functor = functor
        self.terms = terms
        if terms != None and len(terms) > 0:
            self.terms = terms
    
    def arity(self):
        """ functorの引数の数 """
        return len(self.terms)
    
    def canFindNextProof(self):
        return False
    
    def copyForProof(self, _as, scope):
        newTerms = []
        for t in self.terms:
            newTerms.append(t.copyForProof(_as, scope))
        # ConsultingStructureを直接使えないので、クラス名からインスタンスを生成
        cls = globals()['ConsultingStructure']
        return cls(_as, self.functor, newTerms)
    
    def __eq__(self, o):
        if type(self) != type(o):
            return False
        s = o
        if not self.functorAndArityEquals(s):
            return False
        for i in range(self.arity()):
            if not self.terms[i].__eq__(s.terms[i]):
                return False
        return True
    
    def functorAndArityEquals(self, s):
        return self.arity() == s.arity() and self.functor.__eq__(s.functor)
    
    def unify(self, s):
        if isinstance(s, Structure):
            if not self.functorAndArityEquals(s):
                return None
            u = Unification()
            others = s.terms
            for i in range(len(self.terms)):
                subUnification = self.terms[i].unify(others[i])            
                if subUnification == None:
                    u.unbind()
                    return None
                u.append(subUnification)
            return u
        elif isinstance(s, Variable):
            v = s
            return v.unify(self)
        else: # Term
            t = s
            return t.unify(self)
    
    def eval(self):
        if len(self.terms) > 0:
            return self
        return self.functor
    
    def __str__(self):
        if self.isList():
            return f"[{self.listTermsToString()}]"
        buf = str(self.functor)
        if self.terms != None and len(self.terms) > 0:
            buf += "("
            for i in range(len(self.terms)):
                if i > 0:
                    buf += ", "
                buf += self.terms[i].__str__()
            buf += ")"
        return buf
    
    def variables(self):
        u = Unification()
        if len(self.terms) > 0:
            for t in self.terms:
                u.append(t.variables())
        return u

class Scope:
    def __init__(self, terms=[]):
        self.dictionary = {}
        for t in terms:
            u = t.variables()
            for v in u.elements():
                self.dictionary[v.name] = v
    
    def clear(self):
        self.dictionary.clear()

    def lookup(self, name):
        v = self.dictionary.get(name)
        if v == None:
            v = Variable(name)
            self.dictionary[name] = v
        return v

class Rule:
    def __init__(self, structures=[]):
        self.structures = structures

    def dynamicAxiom(self, axiomSource):
        return DynamicRule(axiomSource, Scope(), self)
    
    def head(self):
        return self.structures[0]
    
    def __eq__(self, o):
        if not isinstance(o, Rule):
            return False
        r = o
        if len(self.structures) != len(r.structures):
            return False
        for i in range(self.structures):
            if self.structures[i] != r.structures[i]:
                return False
        return True
    
    def __str__(self):
        buf = str("")
        for i in range(len(self.structures)):
            if i == 1:
                buf += " :- "
            if i > 1:
                buf += ", "
            buf += self.structures[i].__str__()
        return buf

class ConsultingStructure(Structure):
    def __init__(self, source, functor, terms=[]):
        super().__init__(functor, terms)
        self.source = source
        self._axioms = None
        self.currentUnification = None
        self.resolvent = None
    
    def axioms(self):
        if self._axioms == None:
            self._axioms = iter(self.source.axioms(self))
        return self._axioms
    
    def canFindNextProof(self):
        if self.resolvent != None:
            if self.resolvent.canFindNextProof():
                return True
        while True:
            self.unbind()
            if not self.canUnify():
                self._axioms = None
                return False
            if self.resolvent.canEstablish():
                if Program.debug:
                    print(f"\tReturn: {self.variables()}")
                return True
    
    def canUnify(self):
        while (a := next(self.axioms(), None)):
            h = a.head()
            if not self.functorAndArityEquals(h):
                continue
            aCopy = a.dynamicAxiom(self.source)
            if Program.debug:
                print(f"\t{h}", end="")
            self.currentUnification = aCopy.head().unify(self)
            self.resolvent = None
            if self.currentUnification != None:
                self.resolvent = aCopy.resolvent()
                # デバッグトレース
                if Program.debug:
                    if not self.resolvent.isEmpty():
                        print(f"\tTrue\t{self.currentUnification} => {self.resolvent}")
                    else:
                        print(f"\tTrue\t{self.currentUnification}")
                return True
            elif Program.debug:
                print(f"\tFalse")
        return False
    
    def unbind(self):
        if self.currentUnification != None:
            self.currentUnification.unbind()
        self.currentUnification = None
        self.resolvent = None


class DynamicRule(Rule):
    def __init__(self, _as, scope, arg):
        if isinstance(arg, Rule):
            rule = arg
            structures = self.provableStructures(_as, scope, rule.structures)
        else:
            structures = arg
        super().__init__(structures)
        self._as = _as
        self.scope = scope
        self._tail = None
        self.headInvolved = False

    def canEstablish(self):
        if self.isEmpty():
            return True
        return self.canFindNextProof()
    
    def canFindNextProof(self):
        if self.isEmpty():
            return False
        
        if self.headInvolved:
            if self.tail().canFindNextProof():
                return True
            
        while True:
            self.headInvolved = self.head().canFindNextProof()
            if not self.headInvolved:
                return False
            if self.tail().canEstablish():
                return True

    def isEmpty(self):
        return len(self.structures) == 0
    

    def provableStructures(self, _as, scope, structures):
        provables = []
        for s in structures:
            if isinstance(s, Fact):
                provables.append(ConsultingStructure(_as, s.functor, s.terms))
            else:
                provables.append(s.copyForProof(_as, scope))
        return provables

    def resolvent(self):
        return self.tail()
    
    def tail(self):
        if self._tail == None:
            rest = copy.copy(self.structures[1:])
            self._tail = DynamicRule(self._as, self.scope, rest)
        return self._tail
    
    def variables(self):
        if len(self.structures) == 0:
            return Unification.empty
        return self.head().variables().append(self.tail().variables())
    

class Fact(Structure):
    _resolvent = DynamicRule(None, None, [])

    @classmethod
    def facts(cls, objects):
        terms = []
        for o in objects:
            terms.append(Atom(o))
        return terms
    
    def __init__(self, functor, *args):
        if len(args) == 0:
            super().__init__(functor)
        elif len(args) == 1:            
            if isinstance(args[0], list):
                first = args[0]
                if len(first) > 0 and isinstance(first[0], Fact):
                    super().__init__(functor, first)
                else:
                    atoms = [Atom(o) for o in first]
                    super().__init__(functor, atoms)
            elif isinstance(args[0], Fact):
                super().__init__(functor, [args[0]])
            else:
                super().__init__(functor, [Atom(args[0])])
        elif len(args) == 2:
            o1 = args[0]
            o2 = args[1]
            if isinstance(o1, Atom):
                super().__init__(functor, [o1, o2])
            else:
                super().__init__(functor, [Atom(o1), Atom(o2)])
    
    def unify(self, f):
        # 注意: fがFactでない場合、superのunifyを呼ぶ
        if not isinstance(f, Fact):
            return super().unify(f)
        if not self.functorAndArityEquals(f):
            return None
        for i in range(len(self.terms)):
            f1 = self.terms[i]
            f2 = f.terms[i]
            if f1.unify(f2) == None:
                return None
        return Unification.empty
    
    def dynamicAxiom(self, ignored):
        return self
    
    def resolvent(self):
        return Fact._resolvent
    
    def head(self):
        return self
    
    def copyForProof(self, ignored, ignored2):
        return self
    
    def dynamicAxiom(self, ignored):
        return self
    
class Atom(Fact):
    def __init(self, functor):
        super().__init__(functor)

    def eval(self):
        return self.functor
    
    def __str__(self):
        if isinstance(self.functor, str) and ' ' in self.functor:
            return f'"{self.functor}"'
        else:
            return super().__str__()

class EmptyList(Fact):
    def __init__(self):
        super().__init__(".")
    
    def isList(self):
        return True
    
    def listTailString(self):
        return ""
    
    def __str__(self):
        return "[]"
    
class Program:
    debug = False
    def __init__(self, axioms=[]):
        self._axioms = None
        self._elements = []
        for axiom in axioms:
            self.addAxiom(axiom)
    
    def addAxiom(self, a):
        self._elements.append(a)

    def append(self, _as):
        e = _as.axioms()
        for a in e:
            self.addAxiom(a)
            
    def axioms(self, *args):
        return iter(self._elements)
    
    def __str__(self):
        buf = str()
        haveShownALine = False
        for e in self.axioms():
            if haveShownALine:
                buf += "\n"
            buf += e.__str__()
            buf += ";"
            haveShownALine = True
        return buf

class Query(DynamicRule):
    def __init__(self, _as, *args):
        self._tail = None
        if len(args) == 1:
            if isinstance(args[0], Rule):
                rule = args[0]
                scope = Scope(rule.structures)
                structures = rule.structures
            else:
                if isinstance(args[0], Structure):
                    structures = [args[0]]
                else:
                    structures = args[0]
                scope = Scope(structures)
        elif len(args) == 2:
            scope = args[0]
            structures = args[1]
        super().__init__(_as, scope, super().provableStructures(_as, scope, structures))
    
    def __str__(self):
        buf = str("")
        for i in range(len(self.structures)):
            if i > 0:
                buf += ", "
            buf += self.structures[i].__str__()
        return buf
    
class Gateway(Structure):
    def __init__(self, functor, terms=[]):
        super().__init__(functor, terms)
        self.open = False
    
    def canFindNextProof(self):
        if self.open:
            self.open = False
        else:
            self.open = self.canProveOnce()
        if not self.open:
            self.cleanup()
        return self.open
    
    def canProveOnce(self):
        return True
    
    def cleanup(self):
        return None

class Comparison(Gateway):
    def __init__(self, operator, term0, term1):
        super().__init__(operator, [term0, term1])
        self.operator = operator
        self.term0 = term0
        self.term1 = term1
    
    def canProveOnce(self):
        p0 = self.term0.eval()
        p1 = self.term1.eval()
        if not self.compare(p0, p1):
            return False
        return True
    
    def compare(self, obj0, obj1):
        if (isinstance(obj0, int) or isinstance(obj0, float)) and (isinstance(obj1, int) or isinstance(obj1, float)):
            return self.compareNumber(obj0, obj1)
        elif isinstance(obj0, str) and isinstance(obj1, str):
            return self.compareString(obj0, obj1)
        else:
            return False
        
    def compareNumber(self, d0, d1):
        if self.operator == ">":
            return d0 > d1
        elif self.operator == "<":
            return d0 < d1
        elif self.operator == "=":
            return d0 == d1
        elif self.operator == ">=":
            return d0 >= d1
        elif self.operator == "<=":
            return d0 <= d1
        elif self.operator == "!=":
            return d0 != d1
        else:
            return False
        
    def compareString(self, s0, s1):
        if self.operator == ">":
            return s0 > s1
        elif self.operator == "<":
            return s0 < s1
        elif self.operator == "=":
            return s0 == s1
        elif self.operator == ">=":
            return s0 >= s1
        elif self.operator == "<=":
            return s0 <= s1
        elif self.operator == "!=":
            return s0 != s1
        else:
            return False

    def copyForProof(self, ignored, scope):
        return Comparison(
            self.operator,
            self.term0.copyForProof(None, scope),
            self.term1.copyForProof(None, scope))
    
    def eval(self):
        return self.canProveOnce()

class ArithmeticOperator(Structure):
    def __init__(self, operator, term0, term1):
        super().__init__(operator, [term0, term1])
        self.operator = operator
        self.term0 = term0
        self.term1 = term1
    
    def arithmeticValue(self, d0, d1):
        result = 0
        if self.operator == "+":
            result = d0 + d1
        elif self.operator == "-":
            result = d0 - d1
        elif self.operator == "*":
            result = d0 * d1
        elif self.operator == "/":
            result = d0 / d1
        elif self.operator == "%":
            result = d0 // d1
        else:
            result = 0.0
        return result

    def copyForProof(self, ignored, scope):
        return ArithmeticOperator(
            self.operator,
            self.term0.copyForProof(None, scope),
            self.term1.copyForProof(None, scope))
    
    def eval(self, *args):
        if len(args) == 0:
            d0 = self.eval(self.term0)
            d1 = self.eval(self.term1)
            return self.arithmeticValue(d0, d1)
        elif len(args) == 1:
            t = args[0]
            o = t.eval()
            if o == None:
                raise Exception(f"{t} is undefined in {self}")
            return o

class Write(Gateway):
    def __init__(self, *args):
        newArgs = []
        for a in list(args):
            if isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
                a = Atom(a)
            newArgs.append(a)
        super().__init__("write", newArgs)
        self.terms = newArgs
        self.currentUnification = None
    
    def canProveOnce(self):
        try:
            for t in self.terms:
                print(t.eval(), end="")
            print("")
        except:
            print("undefined")
            return False
        return True
        
    def copyForProof(self, ignored, scope):
        newTerm = []
        for t in self.terms:
            newTerm.append(t.copyForProof(None, scope))
        return Write(*newTerm)
    
    def eval(self):
        return self.canProveOnce()
    
class Evaluation(Gateway):
    def __init__(self, term0, term1):
        super().__init__("#", [term0, term1])
        self.term0 = term0
        self.term1 = term1
        self.currentUnification = None
    
    def canProveOnce(self):
        try:
            o = self.term1.eval()
        except:
            return False
        self.currentUnification = self.term0.unify(Atom(o))
        return self.currentUnification != None
    
    def cleanup(self):
        self.unbind()

    def copyForProof(self, ignoed, scope):
        return Evaluation(
            self.term0.copyForProof(None, scope),
            self.term1.copyForProof(None, scope)
        )
    
    def unbind(self):
        if self.currentUnification != None:
            self.currentUnification.unbind()
        self.currentUnification = None

class ConsultingNot(Gateway):
    def __init__(self, consultingStructure):
        super().__init__(consultingStructure.functor, consultingStructure.terms)
        self.consultingStructure = consultingStructure

    def canProveOnce(self):
        return not (self.consultingStructure.canUnify() and 
                    self.consultingStructure.resolvent.canEstablish())
    
    def cleanup(self):
        self.consultingStructure.unbind()
        self.consultingStructure._axioms = None

    def __str__(self):
        return f"not {self.consultingStructure}"
    
class Not(Structure):
    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                functor = args[0]
                super().__init__(functor, [])
            elif isinstance(args[0], Structure):
                s = args[0]
                super().__init__(s.functor, s.terms)
        else:
            functor = args[0]
            terms = args[1]
            super().__init__(functor, terms)
    
    def copyForProof(self, _as, scope):
        newTerms = []
        for t in self.terms:
            newTerms.append(t.copyForProof(_as, scope))
        return ConsultingNot(ConsultingStructure(_as, self.functor, newTerms))
    
    def __eq__(self, o):
        if not isinstance(o, Not):
            return False
        n = o
        if not self.functorAndArityEquals(n):
            return False
        for i in range(len(self.terms)):
            if not self.terms[i].__eq__(n.terms[i]):
                return False
        return True
    
    def __str__(self):
        return f"not {super().__str__()}"
    
class Anonymous(Variable):
    def __init__(self):
        super().__init__("_")

    def copyForProof(self, ignored, ignored2):
        return self
    
    def eval(self):
        return self.name
    
    def unify(self, ignored):
        return Unification.empty
    
    def variables(self):
        return Unification.empty

