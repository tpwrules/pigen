Translate Python functions into Migen statements.

Functions are translated in the following manner:
* identity statements `x is y` become `module.comb.<domain> += x.eq(y)` (but not identity expressions!)
* assignment statements `x = y` become `module.sync.<domain> += x.eq(y)`
* if statements become the corresponding objects
* no other statements in the function body are supported
* all Migen expressions are supported

There are four decorators:
* `@pigen.statement(module, domain='sys')`
    Translate the function as described above.
* `@pigen.purecomb(module, domain='sys')`
    Translate the function as described above, but treat any synchronous statements as an error,
* `@pigen.puresync(module, domain='sys')`
    Translate the function as described above, but treat any combinatorial statements as an error.
* `@pigen.fsm(fsm, state)`
    Translate the function as described above, but pass the statements to `fsm.act(state, *statements)` instead of adding them to `self`. Additionally, translate `x = y` to `NextValue(x, y)`.
