from migen import *
import pigen

class FSMTest(Module):
    def __init__(self):
        self.active = Signal()
        self.bitno = Signal(3)
        self.strobe = Signal()

        fsm = FSM(reset_state="START")
        self.submodules += fsm

        fsm.act("START",
            self.active.eq(1),
            If(self.strobe,
                NextState("DATA")
            )
        )
        fsm.act("DATA",
            self.active.eq(1),
            If(self.strobe,
                NextValue(self.bitno, self.bitno + 1),
                If(self.bitno == 7,
                    NextState("END")
                )
            )
        )
        fsm.act("END",
            self.active.eq(0),
            NextState("STOP")
        )
        fsm.act("STOP",
            self.active.eq(0),
            If(self.strobe,
                NextState("START"),
                NextValue(self.bitno, 0)
            )
        )


if __name__ == "__main__":
    from migen.fhdl.verilog import convert
    m = FSMTest()
    convert(m, ios={m.strobe, m.active, m.bitno}).write("demos/fsmtest.v")