from pyUL1741SB.IEEE1547.VoltReg.cpf import CPF
from pyUL1741SB.IEEE1547.VoltReg.crp import CRP
from pyUL1741SB.IEEE1547.VoltReg.vv import VV
from pyUL1741SB.IEEE1547.VoltReg.wv import WV
from pyUL1741SB.IEEE1547.VoltReg.vw import VW

class VoltReg(CPF, VV, WV, CRP, VW):
    pass