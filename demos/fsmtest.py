from migen import *
import pigen

class FSMTest(Module):
    def __init__(self):
        self.active = Signal()
        self.bitno = Signal(3)
        self.strobe = Signal()

        ###

        fsm = FSM(reset_state="START")
        self.submodules += fsm

        @pigen.fsm(fsm, "START")
        def fsm_start():
            self.active is 1
            if self.strobe:
                next_state = "DATA"

        @pigeon.fsm(fsm, "DATA")
        def fsm_data():
            self.active is 1
            if self.strobe:
                self.bitno = self.bitno + 1
                if self.bitno == 7:
                    next_state = "END"

        @pigeon.fsm(fsm, "END")
        def fsm_end():
            self.active is 0
            next_state = "STOP"

        @pigeon.fsm(fsm, "STOP")
        def fsm_stop():
            self.active is 0
            if self.strobe:
                next_state = "START"
                self.bitno = 0


if __name__ == "__main__":
    from migen.fhdl.verilog import convert
    m = FSMTest()
    convert(m, ios={m.strobe, m.active, m.bitno}).write("demos/fsmtest.v")