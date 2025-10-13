"""
IEEE 1547.1-2020 5.16
"""
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve

import pandas as pd

class RespPri:
    """"""
    """
    IEEE 1547.1-2020
    Table 38 — Category A Voltage and Frequency Regulation Priority Test Steps and Expected Results
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+
    | Step | Voltage | Freq    | Active  | volt-var  | var       | PF        | watt-var  |
    |      | (p.u.)  | (Hz)    | Power   | (p.u.)    | (p.u.)    | (unitless)| (p.u.)    |
    |      |         |         | (p.u.)  |           |           |           |           |
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+
    |  1   |   1     |   60    |   0.5   |     0     | 0.44 inj  | 0.9 inj   |     0     |
    |  2   |   1.09  |   60    |   0.4   | 0.25 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  3   |   1.09  |  60.33  |   0.3   | 0.25 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  4   |   1.09  |   60    |   0.4   | 0.25 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  5   |   1.09  |  59.36  |   0.4   | 0.25 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  6   |   1     |  59.36  |   0.6   |     0     | 0.44 inj  | 0.9 inj   | 0.05 abs  |
    |  7   |   1     |   60    |   0.5   |     0     | 0.44 inj  | 0.9 inj   |     0     |
    |  8   |   1     |  59.36  |   0.7   |     0     | 0.44 inj  | 0.9 inj   | 0.10 abs  |
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+

    Table 39 — Category B Voltage and Frequency Regulation Priority Test Steps and Expected Results
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+
    | Step | Voltage | Freq    | Active  | volt-var  | var       | PF        | watt-var  |
    |      | (p.u.)  | (Hz)    | Power   | (p.u.)    | (p.u.)    | (unitless)| (p.u.)    |
    |      |         |         | (p.u.)  |           |           |           |           |
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+
    |  1   |   1     |   60    |   0.5   |     0     | 0.44 inj  | 0.9 inj   |     0     |
    |  2   |   1.09  |   60    |   0.4   | 0.44 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  3   |   1.09  |  60.33  |   0.3   | 0.44 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  4   |   1.09  |   60    |   0.4   | 0.44 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  5   |   1.09  |  59.36  |   0.4   | 0.44 abs  | 0.44 inj  | 0.9 inj   |     0     |
    |  6   |   1     |  59.36  |   0.6   |     0     | 0.44 inj  | 0.9 inj   | 0.09 abs  |
    |  7   |   1     |   60    |   0.5   |     0     | 0.44 inj  | 0.9 inj   |     0     |
    |  8   |   1     |  59.36  |   0.7   |     0     | 0.44 inj  | 0.9 inj   | 0.18 abs  |
    +------+---------+---------+---------+-----------+-----------+-----------+-----------+
    """
    @staticmethod
    def catA():
        data = {
            'step': [1, 2, 3, 4, 5, 6, 7, 8],
            'vpu_ac': [1, 1.09, 1.09, 1.09, 1.09, 1, 1, 1],
            'fhz_ac': [60, 60, 60.33, 60, 59.36, 59.36, 60, 59.36],
            'e_ap_pu': [0.5, 0.4, 0.3, 0.4, 0.4, 0.6, 0.5, 0.7],
            'e_vv_rp_pu': [0, -0.25, -0.25, -0.25, -0.25, 0, 0, 0],
            'e_crp_rp_pu': [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
            'e_cpf_pf': [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
            'e_wv_rp_pu': [0, 0, 0, 0, 0, -0.05, 0, -0.10]
        }
        return pd.DataFrame(data).set_index('step')

    @staticmethod
    def catB():
        data = {
            'step': [1, 2, 3, 4, 5, 6, 7, 8],
            'vpu_ac': [1, 1.09, 1.09, 1.09, 1.09, 1, 1, 1],
            'fhz_ac': [60, 60, 60.33, 60, 59.36, 59.36, 60, 59.36],
            'e_ap_pu': [0.5, 0.4, 0.3, 0.4, 0.4, 0.6, 0.5, 0.7],
            'e_vv_rp_pu': [0, -0.44, -0.44, -0.44, -0.44, 0, 0, 0],
            'e_crp_rp_pu': [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
            'e_cpf_pf': [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
            'e_wv_rp_pu': [0, 0, 0, 0, 0, -0.09, 0, -0.18]
        }
        return pd.DataFrame(data).set_index('step')
