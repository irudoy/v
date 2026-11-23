# Bounded JK08A coordinate sample argument

Source bindings: `JK08A.closed-loop-sample-argument.toml`.

The real caller0003EDB4 loads the word at0003EE72. BSR0003EE7A executes
MOV R0,R6 at0003EE7C, passing the sign-extended word in the actual R6
callee-entry state. The natural conditioner zero-extends this argument,
uses its high byte in the coefficient lookup and its complete unsigned
word in the strict admission comparisons.
