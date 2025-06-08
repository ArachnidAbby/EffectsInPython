from contextlib import contextmanager
from typing import Any


EFFECT_CONTEXT_STACK: dict[Any, list] = {}


def reset_globals(func, new_globals, previous_globals):
    for name in new_globals.keys():
        del func.__globals__[name]
    for name, some_val in previous_globals.items():
        func.__globals__[name] = some_val


@contextmanager
def add_to_effect_stack(effect, implementation):
    if effect not in EFFECT_CONTEXT_STACK.keys():
        EFFECT_CONTEXT_STACK[effect] = []
    EFFECT_CONTEXT_STACK[effect].append(implementation)
    try:
        yield
    finally:
        EFFECT_CONTEXT_STACK[effect].pop(-1)


class Effect:
    """describes an effect"""

    def __init__(self, *funcs):
        self.names = [func.__name__ for func in funcs]


class EffectImplementation:
    """Describes an implementation of an effect"""

    def __init__(self, effect, functions):
        self.effect = effect
        self.functions = functions

    def function_descriptions(self, previous_globals):
        output = {}
        for name, func in self.functions.items():

            def wrapper(*args, **kwargs):
                new_globals = func.__globals__
                for _name in self.functions.keys():
                    del func.__globals__[_name]
                for _name, some_val in previous_globals.items():
                    func.__globals__[_name] = some_val
                try:
                    output = func(*args, **kwargs)
                finally:
                    for name, special_func in new_globals.items():
                        func.__globals__[name] = special_func
                return output

            output[name] = wrapper
        return output


def ImplementEffect(effect, **kwargs):
    """create an implementation of an effect"""
    implementation = EffectImplementation(effect, kwargs)

    def wrapper(func):
        def inner():
            # TODO: Make this a context manager for correctness
            with add_to_effect_stack(effect, implementation):
                output = func()
            return output

        return inner

    return wrapper


class EffectNotImplemented(Exception):
    pass


def UsingEffect(effect_descriptor: Effect):
    def wrapper(func):
        def inner(*args, **kwargs):
            if (
                effect_descriptor not in EFFECT_CONTEXT_STACK
                or len(EFFECT_CONTEXT_STACK[effect_descriptor]) == 0
            ):
                raise EffectNotImplemented()
            effect_implementor = EFFECT_CONTEXT_STACK[effect_descriptor][-1]
            previous_globals = {**func.__globals__}

            # modify function globals
            for name, special_func in effect_implementor.function_descriptions(
                previous_globals
            ).items():
                func.__globals__[name] = special_func
            try:
                func_val = func(*args, **kwargs)
            finally:
                reset_globals(func, effect_implementor.functions, previous_globals)
            return func_val

        return inner

    return wrapper


def EffectFunction(func):
    """create a function to be used in an effect"""

    def wrapper(*args, **kwargs):
        raise NameError(f"name '{func.__name__}' is not defined")

    return wrapper
