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
        return statements

    statements = parse_body(fn_body)
        
    print(statements)

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