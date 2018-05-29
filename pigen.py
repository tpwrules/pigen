import migen

import ast
import inspect

__all__ = ["statement", "purecomb", "puresync", "fsm"]

# the provided decorators
# todo: write real docstrings

def statement(domain='sys'):
    def decorator(fn):
        _translate(fn, domain, comb_allowed=True, sync_allowed=True)
        return None # no real use for calling once it's been translated
    return decorator

def purecomb(domain='sys'):
    def decorator(fn):
        _translate(fn, domain, comb_allowed=True, sync_allowed=False)
        return None # no real use for calling once it's been translated
    return decorator

def puresync(domain='sys'):
    def decorator(fn):
        _translate(fn, domain, comb_allowed=False, sync_allowed=True)
        return None # no real use for calling once it's been translated
    return decorator

def fsm(fsm, state):
    def decorator(fn):
        _translate(fn, None, comb_allowed=True, sync_allowed=True, fsm=(fsm, state))
        return None # no real use for calling once it's been translated
    return decorator

class TranslationError(Exception):
    pass

def _translate(input_fn, domain=None, comb_allowed=True, sync_allowed=True, fsm=None):
    # do the translation magic!

    if not inspect.isfunction(input_fn):
        raise TranslationError(
            "can only translate functions, not: {}".format(type(input_fn)))

    # STEP 1: recover the AST of the input function

    tree = _get_ast(input_fn)
    print(ast.dump(tree))
    
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