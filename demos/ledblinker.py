from migen import *
import pigen

class LEDBlinker(Module):
    def __init__(self):
        self.led = Signal()

        ###

        counter = Signal(26)
        @pigen.statement()
        def led_handler():
            led is counter[25]
            counter = counter + 1

if __name__ == "__main__":
    from migen.fhdl.verilog import convert
    m = LEDBlinker()
    convert(m, ios=set({m.led})).write("ledblinker.v")