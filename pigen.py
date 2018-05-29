import migen

import ast
import inspect

__all__ = ["statement", "purecomb", "puresync", "fsm"]

# the provided decorators
# todo: write real docstrings

def statement(module, domain='sys'):
    def decorator(fn):
        _translate(fn, module, domain, comb_allowed=True, sync_allowed=True)
        return None # no real use for calling once it's been translated
    return decorator

def purecomb(module, domain='sys'):
    def decorator(fn):
        _translate(fn, module, domain, comb_allowed=True, sync_allowed=False)
        return None # no real use for calling once it's been translated
    return decorator

def puresync(module, domain='sys'):
    def decorator(fn):
        _translate(fn, module, domain, comb_allowed=False, sync_allowed=True)
        return None # no real use for calling once it's been translated
    return decorator

def fsm(fsm, state):
    def decorator(fn):
        _translate(fn, None, None, comb_allowed=True, sync_allowed=True, fsm=(fsm, state))
        return None # no real use for calling once it's been translated
    return decorator

class TranslationError(Exception):
    pass

def _translate(input_fn, module, domain, comb_allowed, sync_allowed, fsm=None):
    # do the translation magic!

    if not inspect.isfunction(input_fn):
        raise TranslationError(
            "can only translate functions, not: {}".format(type(input_fn)))

    # STEP 1: recover the AST of the input function
    tree = _get_ast(input_fn)
    # get the body of the function as the tree
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fn_body = node.body
            break
    else:
        raise TranslationError("could not find function def")

    # STEP 2: derive statements from AST

    def parse_body(body, kind=None):
        statements = []
        for stmt in body:
            if isinstance(stmt, ast.Expr):
                # miiiight be a combinatorial assign
                if not isinstance(stmt.value, ast.Compare):
                    raise TranslationError("bare expr is not Compare")
                stmt = stmt.value
                if len(stmt.ops) != 1 or not isinstance(stmt.ops[0], ast.Is):
                    raise TranslationError("bare expr is not 'is'")
                # ah, it is
                statements.append(("comb", stmt.left, stmt.comparators[0]))
                if kind == "sync" and fsm is None:
                    raise TranslationError("mixing comb and sync inside if")
                if kind is not None:
                    kind = "comb"
            elif isinstance(stmt, ast.Assign):
                # an assignment statement, this must be synchronous
                # extract the dest and src
                if len(stmt.targets) != 1:
                    raise TranslationError(
                        "assignment has {} targets, not supported".format(
                            len(stmt.targets)))
                dest = stmt.targets[0]
                src = stmt.value
                statements.append(("sync", dest, src))
                if kind == "comb" and fsm is None:
                    raise TranslationError("mixing comb and sync inside if")
                if kind is not None:
                    kind = "sync"
            elif isinstance(stmt, ast.If):
                # what we are predicating on
                test = stmt.test
                if_true, true_kind = parse_body(stmt.body, "if")
                if_false, false_kind = parse_body(stmt.orelse, "else")
                if true_kind == "if": continue
                if false_kind != "else" and true_kind != false_kind and fsm is None:
                    raise TranslationError("mixing comb and sync across if/else")
                statements.append(("if", true_kind, test, if_true, if_false))
            elif isinstance(stmt, ast.Nonlocal):
                continue
            else:
                raise TranslationError("invalid statement {}".format(stmt))
        return statements, kind

    statements, _ = parse_body(fn_body)

    # STEP 3: execute statements

    # first a little work: derive the context in which the original function ran
    orig_globals = input_fn.__globals__ # that one was easy
    orig_locals = {}
    for name, val in zip(input_fn.__code__.co_freevars, input_fn.__closure__):
        orig_locals[name] = val.cell_contents

    # we also need a thing which turns store context into load
    def makeload(v):
        for node in ast.walk(v):
            if hasattr(node, 'ctx'):
                node.ctx = ast.Load()

    # and something to return the result of an arbitrary AST expression
    def ast_eval(tree):
        # wrap it in an expression
        tree = ast.Expression(tree)
        # stop the compiler whining
        ast.fix_missing_locations(tree)
        # compile it into a code object
        code = compile(tree, filename="<pigen>", mode="eval")
        # and return the result of it running
        return eval(code, orig_globals, orig_locals)

    def exec_stmts(stmts):
        results = []
        for stmt in stmts:
            # now execute the statements
            if stmt[0] == "comb" or stmt[0] == "sync":
                # we need to evalue x.eq(y)
                # so do x and y first
                makeload(stmt[1]) # after a little hack
                x, y = ast_eval(stmt[1]), ast_eval(stmt[2])
                # now execute x.eq(y) and save the result
                results.append((stmt[0], x.eq(y)))
            elif stmt[0] == "if":
                # execute the predicate
                pred = ast_eval(stmt[2])
                # get results of substatements
                if_true = tuple(r[1] for r in exec_stmts(stmt[3]))
                if_false = tuple(r[1] for r in exec_stmts(stmt[4]))
                the_if = migen.If(pred, *if_true)
                if len(if_false) > 0:
                    the_if = the_if.Else(*if_false)
                results.append((stmt[1], the_if))
        return results

    # add top level results to module
    if fsm is None:
        results = exec_stmts(statements)
        for result in results:
            # of course, now we have to add that to the module
            cs = getattr(module, result[0])
            if domain != "sys":
                cs = getattr(module, domain)
            cs += result[1]


def _get_ast(fn):
    # get the AST for a given function

    # we first have to recover the source
    try:
        src_lines, _ = inspect.getsourcelines(fn)
    except:
        raise TranslationError("could not retrieve function source")

    # clean up the source by removing the decorator and despacing it
    if src_lines[0].strip().startswith("@"):
        src_lines = src_lines[1:]
    leading_spaces = len(src_lines[0]) - len(src_lines[0].lstrip())
    src = ""
    for line in src_lines:
        src += line[leading_spaces:]

    # now that we have that, compile it into an AST
    try:
        tree = ast.parse(src)
    except:
        raise TranslationError("could not generate AST")

    return tree