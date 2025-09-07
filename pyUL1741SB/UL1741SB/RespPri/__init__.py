"""
IEEE 1547.1-2020 5.16
"""
import pandas as pd

from pyUL1741SB.env import Env
from pyUL1741SB.eut import Eut
from pyUL1741SB.IEEE1547.FreqSupp import FW_OF, FW_UF
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve

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
    iVolts_key = 'Voltage (p.u.)'
    iFreq_key = 'Frequency (Hz)'
    oWatts_key = 'Active Power (p.u.)'
    oVV_key = 'volt-var (p.u.)'
    oVar_key = 'Active Power (p.u.)'
    oPF_key = 'Power Factor'
    oWV_key = 'watt-var (p.u.)'
    # Create DataFrames
    df_catApri = pd.DataFrame({
        'Step': [1, 2, 3, 4, 5, 6, 7, 8],
        iVolts_key: [1.0, 1.09, 1.09, 1.09, 1.09, 1.0, 1.0, 1.0],
        iFreq_key: [60.0, 60.0, 60.33, 60.0, 59.36, 59.36, 60.0, 59.36],
        oWatts_key: [0.5, 0.4, 0.3, 0.4, 0.4, 0.6, 0.5, 0.7],
        oVV_key: [0.0, -0.25, -0.25, -0.25, -0.25, 0.0, 0.0, 0.0],
        oVar_key: [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
        oPF_key: [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        oWV_key: [0.0, 0.0, 0.0, 0.0, 0.0, -0.05, 0.0, -0.10]
    })
    df_catBpri = pd.DataFrame({
        'Step': [1, 2, 3, 4, 5, 6, 7, 8],
        iVolts_key: [1.0, 1.09, 1.09, 1.09, 1.09, 1.0, 1.0, 1.0],
        iFreq_key: [60.0, 60.0, 60.33, 60.0, 59.36, 59.36, 60.0, 59.36],
        oWatts_key: [0.5, 0.25, 0.15, 0.25, 0.25, 0.5, 0.5, 0.7],
        oVV_key: [0.0, -0.44, -0.44, -0.44, -0.44, 0.0, 0.0, 0.0],
        oVar_key: [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
        oPF_key: [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        oWV_key: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.18]
    })
    df_catApri.set_index('Step', inplace=True)
    df_catBpri.set_index('Step', inplace=True)
