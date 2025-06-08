from functools import wraps
from typing import Any
from effects import UsingEffect, ImplementEffect, EffectFunction, Effect


@EffectFunction
def next() -> Any:
    pass


@EffectFunction
def should_iter() -> bool:
    return False


Generator = Effect(next, should_iter)


@EffectFunction
def on_iteration(value: Any):
    pass


Loop = Effect(on_iteration)


def main():
    state = [-1]  # mutable state accessible in functions. yay

    def my_range():
        state[0] += 1
        return state[0]

    def should_iter() -> bool:
        return state[0] < 20

    def create_loop():

        @ImplementEffect(
            Generator,
            should_iter=should_iter,
            next=my_range,
        )
        def wrapper():
            @UsingEffect(Loop)
            def iterate():
                @UsingEffect(Generator)
                def secondary_wrapper():
                    on_iteration(next())
                    if should_iter():
                        iterate()

                return secondary_wrapper()

            return iterate()

        return wrapper

    def on_iteration(value):
        print("next value is:", value)

    @ImplementEffect(Loop, on_iteration=on_iteration)
    def do_looping():
        iterator = create_loop()
        iterator()

    return do_looping()


main()
