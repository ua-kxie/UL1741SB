"""
IEEE 1547.1-2020 5.13
"""

from pyUL1741SB.IEEE1547.VoltReg import VoltReg
from pyUL1741SB.IEEE1547.FreqDistResp import FreqDist
from pyUL1741SB.IEEE1547.VoltDistResp import VoltDist

from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve

class IEEE1547(VoltReg, FreqDist, VoltDist):
    pass
