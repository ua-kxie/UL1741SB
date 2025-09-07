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
        oWatts_key: [0.5, 0.4, 0.3, 0.4, 0.4, 0.6, 0.5, 0.7],
        oVV_key: [0.0, -0.44, -0.44, -0.44, -0.44, 0.0, 0.0, 0.0],
        oVar_key: [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
        oPF_key: [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
        oWV_key: [0.0, 0.0, 0.0, 0.0, 0.0, -0.09, 0.0, -0.18]
    })
    df_catApri.set_index('Step', inplace=True)
    df_catBpri.set_index('Step', inplace=True)

    def pri_proc(self, env: Env, eut: Eut):
        """"""
        df_steps = self.df_catApri if eut.Cat == Eut.Category.A else self.df_catBpri
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage and frequency trip parameters to the widest range of adjustability. Disable all
        reactive/active power control functions.
        '''
        '''
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        env.ac_config(Vac=eut.VN, Freq=eut.fN)
        '''
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom.
        '''
        env.dc_config(Vin=eut.VN)
        eut.active_power(WlimPct=100)
        '''
        e) Set EUT frequency-watt and volt-watt parameters to the default values for the EUT’s category, and
        enable frequency-watt and volt-watt parameters. For volt-watt, set P2 = 0.2Prated.
        '''
        if eut.aopCat == Eut.AOPCat.I:
            fwof_char = FW_OF.CatI_CharI()
            fwuf_char = FW_UF.CatI_CharI()
        elif eut.aopCat == Eut.AOPCat.II:
            fwof_char = FW_OF.CatII_CharI()
            fwuf_char = FW_UF.CatII_CharI()
        elif eut.aopCat == Eut.AOPCat.III:
            fwof_char = FW_OF.CatIII_CharI()
            fwuf_char = FW_UF.CatIII_CharI()

        if eut.Cat == Eut.Category.A:
            vwcrv = VWCurve.Crv_1A(eut.Prated, eut.Pmin, eut.VN)
            vwcrv.P2_prime = 0  # 1741 amendment
        elif eut.Cat == Eut.Category.B:
            vwcrv = VWCurve.Crv_1B(eut.Prated, eut.Pmin, eut.VN)
            vwcrv.P2_prime = 0  # 1741 amendment
        '''
        f) Set EUT volt-var parameters to the default values for the EUT’s category and enable volt-var
        mode.
        [...]
        o) Set the constant reactive power function to produce Qmax,inj. Disable the present mode of reactive
        power control and enable constant reactive power mode. Repeat steps g) through n).
        p) Set the constant power factor function to PFmax,inj. Disable the present mode of reactive power
        control and enable power factor mode. Repeat steps g) through n).
        q) Set EUT watt-var parameters to the default values for the EUT’s category. Disable the present
        mode of reactive power control and enable watt-var mode. Repeat steps g) through n).
        '''
        def vv_cfg():
            if eut.Cat == Eut.Category.A:
                vvcrv = VVCurve.Crv_1A(eut.Prated, eut.VN)
            elif eut.Cat == Eut.Category.B:
                vvcrv = VVCurve.Crv_1B(eut.Prated, eut.VN)

        def crp_cfg():
            # disable vvcrv
            eut.reactive_power(Ena=True, eut.Qrated_inj)

        def cpf_cfg():
            eut.reactive_power(Ena=False)
            eut.fixed_pf(Ena=True, PFmaxinj)

        def wv_cfg():
            eut.fixed_pf(Ena=False)
            if eut.Cat == Eut.Category.A:
                wvcrv = WVCurve.Crv_1A(eut.Prated, eut.Pmin, eut.Srated, eut.Prated_prime, eut.Pmin_prime)
            elif eut.Cat == Eut.Category.B:
                wvcrv = WVCurve.Crv_1B(eut.Prated, eut.Pmin, eut.Srated, eut.Prated_prime, eut.Pmin_prime)
        cfgs = [(RespPri.oVV_key, vv_cfg), (RespPri.oVar_key, crp_cfg), (RespPri.oPF_key, cpf_cfg), (RespPri.oWV_key, wv_cfg)]
        for vars_key, cfg in cfgs:
            cfg()
            '''
            g) Allow the EUT to reach steady state. Measure ac test source voltage and frequency and the EUT’s
            active and reactive power production.
            h) Set the EUT’s active power limit signal to 50% of Prated.
            i) Allow the EUT to reach steady state.
            j) Measure ac test source voltage and frequency, and the EUT’s active and reactive power production.
            '''
            eut.active_power(WlimPct=50)
            '''
            n) Repeat steps k) through m) for the rest of the steps in Table 38 or Table 39, depending on the
            EUT’s normal operating performance category.
            '''
            for step, stepvals in df_steps.itertuples():
                '''
                k) Set the ac test source voltage and frequency to the values in step (n) of Table 38 or Table 39,
                depending on the EUT’s normal operating performance category.
                l) Allow the EUT to reach steady state.
                m) Measure ac test source voltage and frequency, and the EUT’s active and reactive power production.
                '''
                env.ac_config(Vac=stepvals[RespPri.iVolts_key], Freq=stepvals[RespPri.iFreq_key])
                stepvals[RespPri.oWatts_key]  # expected active power
                stepvals[vars_key]  # expected reactive power

            raise NotImplementedError
