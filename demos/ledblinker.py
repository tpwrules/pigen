from migen import *
import pigen

class LEDBlinker(Module):
    def __init__(self):
        self.led = Signal()
        self.cspl = Signal()
        self.sspl = Signal()

        ###

        counter = Signal(26)

        @pigen.statement(self)
        def led_handler():
            nonlocal counter
            self.led is counter[25]
            counter = counter + 1
            if counter == 37:
                self.cspl is True
            if counter == 572:
                self.sspl = True
            elif counter == 999:
                self.sspl = False


if __name__ == "__main__":
    from migen.fhdl.verilog import convert
    m = LEDBlinker()
    convert(m, ios={m.led, m.cspl, m.sspl}).write("demos/ledblinker.v")