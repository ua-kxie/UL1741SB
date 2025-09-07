"""
IEEE 1547.1-2020 5.15
"""
class FW_OF:
    def __init__(self, dbof_hz, kof, tr):
        self.dbof_hz = dbof_hz
        self.kof = kof
        self.tr = tr

    @staticmethod
    def CatI_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatII_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatIII_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatI_CharII(): return FW_OF(dbof_hz=0.017, kof=0.03, tr=1)
    @staticmethod
    def CatII_CharII(): return FW_OF(dbof_hz=0.017, kof=0.03, tr=1)
    @staticmethod
    def CatIII_CharII(): return FW_OF(dbof_hz=0.017, kof=0.02, tr=0.2)

class FW_UF:
    def __init__(self, dbuf_hz, kuf, tr):
        self.dbuf_hz = dbuf_hz
        self.kuf = kuf
        self.tr = tr

    @staticmethod
    def CatI_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatII_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatIII_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatI_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatII_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatIII_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.02, tr=0.2)

'''
The manufacturer shall state the following parameters of the EUT for this test:
Prated – Output power rating (W)
fN – Nominal frequency (Hz)
fH – Maximum frequency in the continuous operating region (Hz)
fL – Minimum frequency in the continuous operating region (Hz)
delta_Psmall – Small-signal performance (W)
delta_Plarge – Large-signal performance in % of rated power per minute
EUT’s abnormal operating performance category defined by IEEE Std 1547-2018
The additional parameter shall be calculated as follows:
delta_fsmall = delta_Psmall * fN * kOF
'''