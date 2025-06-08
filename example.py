from effects import UsingEffect, ImplementEffect, EffectFunction

@EffectFunction
def output(_: str):
    pass


MyEffect = Effect(output)


@UsingEffect(MyEffect)
def funny():
    output("some value")
    return 10


@UsingEffect(MyEffect)
def funny2():
    @ImplementEffect(MyEffect, output=lambda x: print(output(x)))
    def try_nesting():
        return funny()

    return try_nesting()


@ImplementEffect(MyEffect, output=lambda x: print(f'we outputed "{x}"!') or 69)
def function_with_effect_handlers():
    print(funny2())


function_with_effect_handlers()

# should output the following
'''
we outputed "some value"!
69
10
'''
