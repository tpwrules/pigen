from migen import *

class LEDBlinker(Module):
    def __init__(self):
        self.led = Signal()

        ###

        counter = Signal(26)
        self.comb += self.led.eq(counter[25])
        self.sync += counter.eq(counter + 1)

if __name__ == "__main__":
    from migen.fhdl.verilog import convert
    m = LEDBlinker()
    convert(m, ios=set({m.led})).write("ledblinker.v")