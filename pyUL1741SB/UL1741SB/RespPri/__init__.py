"""
IEEE 1547.1-2020 5.16
"""
import pandas as pd

from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.RespPri import RespPri
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve

from datetime import timedelta
from typing import Callable

class RespPri1741(RespPri):
    """"""
    @staticmethod
    def catB():
        data = {
            'step': [1, 2, 3, 4, 5, 6, 7, 8],
            'vpu_ac': [1, 1.09, 1.09, 1.09, 1.09, 1, 1, 1],
            'fhz_ac': [60, 60, 60.33, 60, 59.36, 59.36, 60, 59.36],
            'e_ap_pu': [0.5, 0.25, 0.15, 0.25, 0.25, 0.5, 0.5, 0.7],
            'e_vv_rp_pu': [0, -0.44, -0.44, -0.44, -0.44, 0, 0, 0],
            'e_crp_rp_pu': [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
            'e_cpf_pf': [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
            'e_wv_rp_pu': [0, 0, 0, 0, 0, 0, 0, -0.18]
        }
        return pd.DataFrame(data).set_index('step')

    def pri_proc(self, env: Env, eut: Eut):
        """"""
        df_steps = self.catA() if eut.Cat == Eut.Category.A else self.catB()
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage and frequency trip parameters to the widest range of adjustability. Disable all
        reactive/active power control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        env.ac_config(Vac=eut.VN, freq=eut.fN, rocof=eut.rocof())
        '''
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom.
        '''
        eut.set_ap(Ena=True, pu=1)
        '''
        e) Set EUT frequency-watt and volt-watt parameters to the default values for the EUT’s category, and
        enable frequency-watt and volt-watt parameters. For volt-watt, set P2 = 0.2Prated. (P2 = 0.0 1741 amendment)
        [...]
        '''
        if eut.aopCat == Eut.AOPCat.I:
            fwchar = FWChar.CatI_CharI()
        elif eut.aopCat == Eut.AOPCat.II:
            fwchar = FWChar.CatII_CharI()
        elif eut.aopCat == Eut.AOPCat.III:
            fwchar = FWChar.CatIII_CharI()
        else:
            raise TypeError(eut.aopCat)

        if eut.Cat == Eut.Category.A:
            vwcrv = VWCurve.Crv_1A_inj(eut)
            vvcrv = VVCurve.Crv_1A()
            wvcrv = WVCurve.Crv_1A(eut)
        elif eut.Cat == Eut.Category.B:
            vwcrv = VWCurve.Crv_1B_inj(eut)
            vvcrv = VVCurve.Crv_1B()
            wvcrv = WVCurve.Crv_1B(eut)
        else:
            raise TypeError(eut.Cat)
        vwcrv.P2 = 0  # 1741 amendment

        eut.set_fw(Ena=True, crv=fwchar)
        eut.set_vw(Ena=True, crv=vwcrv)
        '''
        f) Set EUT volt-var parameters to the default values for the EUT’s category and enable volt-var
        mode.
        o) Set the constant reactive power function to produce Qmax,inj. Disable the present mode of reactive
        power control and enable constant reactive power mode. Repeat steps g) through n).
        p) Set the constant power factor function to PFmax,inj. Disable the present mode of reactive power
        control and enable power factor mode. Repeat steps g) through n).
        q) Set EUT watt-var parameters to the default values for the EUT’s category. Disable the present
        mode of reactive power control and enable watt-var mode. Repeat steps g) through n).
        '''
        def vv_cfg():
            eut.set_vv(Ena=True, crv=vvcrv)

        def crp_cfg():
            eut.set_vv(Ena=False)
            eut.set_crp(Ena=True, pu=0.44 * eut.Prated / eut.Srated)

        def cpf_cfg():
            eut.set_crp(Ena=False)
            eut.set_cpf(Ena=True, PF=0.9)  # always 0.9

        def wv_cfg():
            eut.set_cpf(Ena=False)
            eut.set_wv(Ena=True, crv=wvcrv)

        cfgs = [('e_vv_rp_pu', vv_cfg), ('e_crp_rp_pu', crp_cfg), ('e_cpf_pf', cpf_cfg), ('e_wv_rp_pu', wv_cfg)]
        for vars_key, cfg in cfgs:
            cfg()
            '''
            g) Allow the EUT to reach steady state. Measure ac test source voltage and frequency and the EUT’s
            active and reactive power production.
            h) Set the EUT’s active power limit signal to 50% of Prated.
            i) Allow the EUT to reach steady state.
            j) Measure ac test source voltage and frequency, and the EUT’s active and reactive power production.
            '''
            eut.set_ap(Ena=True, pu=0.5)
            env.sleep(timedelta(seconds=eut.olrt.lap))
            # meas vac, fac, p, q
            '''
            n) Repeat steps k) through m) for the rest of the steps in Table 38 or Table 39, depending on the
            EUT’s normal operating performance category.
            '''
            for step, row in df_steps.iterrows():
                '''
                k) Set the ac test source voltage and frequency to the values in step (n) of Table 38 or Table 39,
                depending on the EUT’s normal operating performance category.
                l) Allow the EUT to reach steady state.
                m) Measure ac test source voltage and frequency, and the EUT’s active and reactive power production.
                '''
                # tr, x, xMRA, y_of_x(tbl38/39 values)
                def pf_of_x(x):
                    return x * (1 / (row['e_cpf_pf'])**2 - 1) ** 0.5

                dct_q_tup = {
                    'e_vv_rp_pu': (vvcrv.Tr, 'V', eut.mra.static.V, lambda x: row['e_vv_rp_pu'] * eut.Prated),
                    'e_crp_rp_pu': (eut.olrt.crp, 'Q', eut.mra.static.Q, lambda x: row['e_crp_rp_pu'] * eut.Prated),
                    'e_cpf_pf': (eut.olrt.cpf, 'P', eut.mra.static.P, pf_of_x),
                    'e_wv_rp_pu': (eut.olrt.wv, 'V', eut.mra.static.V, lambda x: row['e_wv_rp_pu'] * eut.Prated),
                }
                olrt = timedelta(seconds=max(fwchar.tr, vwcrv.Tr, dct_q_tup[vars_key][0]))
                perturbation = lambda: env.ac_config(Vac=row['vpu_ac'] * eut.VN, freq=row['fhz_ac'])
                dct_label = {
                    'proc': 'pri',
                    'vars_ctrl': vars_key,
                    'step': step,
                }
                self.pri_validation(env, eut, dct_label, row, olrt, perturbation, dct_q_tup[vars_key][3], dct_q_tup[vars_key][1], dct_q_tup[vars_key][2])

    def pri_validation(self, env: Env, eut: Eut, dct_label, df_steprow, olrt, perturb, q_of_x, qx, qxMRA):
        """"""
        """
        5.16.1.4 Criteria
        By deliberately choosing operating points that exercise the simultaneous operation of multiple functions,
        data from this test is used to check the prioritization of functions. After each step, a new steady-state active
        power, Pfinal; reactive power, Qfinal; steady-state voltage, Vsteady; and steady-state frequency Fsteady is
        measured. To obtain a steady-state value, measurements shall be taken after a time period much larger than
        any of the function’s open loop response time. As a guideline, at 2 times the open loop response time
        setting, the steady-state state error is 1%. In addition, instrumentation filtering may be used to reject any
        variation in ac test source voltage during steady-state measurement.
        
        The expected Pfinal and Qfinal are outlined in Table 38 or Table 39, depending on the EUT’s normal
        operating performance category. The expected Qfinal, outlined in Table 38 and Table 39 changes depending
        on which reactive power mode is under test. The values in Table 38 and Table 39 represent the expected
        values based on the voltage and frequency settings; the criteria are evaluated using the measured voltage
        and frequency, as stated below.
        
        Pfinal shall meet the test result accuracy requirements specified in 4.2 where Pfinal is the Y parameter and
        Vsteady or Fsteady is the X parameter, depending on which X parameters gives the largest error margin.
        
        With volt-var enabled, Qfinal shall meet the test result accuracy requirements specified in 4.2 where Qfinal is
        the Y parameter and Vsteady is the X parameter.
        
        With constant reactive power mode enabled, Qfinal shall meet the test result accuracy requirements specified
        in 4.2.
        
        With power factor mode enabled, Qfinal shall meet the test result accuracy requirements specified in 4.2
        where Qfinal is the Y parameter and Psteady is the X parameter. The relationship between active and reactive
        power for constant power factor is given by the following equation:
        Q(P) = Q * sqrt(1/PF**2-1)
        
        With watt-var enabled, Qfinal shall meet the test result accuracy requirements specified in 4.2 where Qfinal is
        the Y parameter and Psteady is the X parameter.
        """
        # meas vac, fac, p, q
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, ('V', 'F', 'P', 'Q'))
        row_ss = df_meas.loc[df_meas.index[0] + olrt:, :].mean()
        p_target = df_steprow['e_ap_pu'] * eut.Prated

        # ap validation
        fwmin, fwmax = self.range_4p2(lambda x: p_target, 0, eut.mra.static.F, eut.mra.static.P)
        vwmin, vwmax = self.range_4p2(lambda x: p_target, 0, eut.mra.static.V, eut.mra.static.P)
        pmin, pmax = min(fwmin, vwmin), max(fwmax, vwmax)
        p_valid = pmin < row_ss['P'] < pmax

        # vv, crp, cpf, wv
        # vv: x is V
        # crp: x is Qset
        # cpf: x is P
        # wv: x is P
        q_target = q_of_x(row_ss[qx])
        qmin, qmax = self.range_4p2(q_of_x, row_ss[qx], qxMRA, eut.mra.static.Q)
        q_valid = qmin < row_ss['Q'] < qmax

        df_meas['p_target'] = p_target
        df_meas['q_target'] = q_target
        env.validate(dct_label={
            **dct_label,
            'p_meas': row_ss['P'],
            'p_target': p_target,
            'p_valid': p_valid,
            'q_meas': row_ss['Q'],
            'q_target': q_target,
            'q_valid': q_valid,
            'data': df_meas
        })

    def vv_wv_validate(self, env: Env, eut: Eut, dct_label: dict, df_meas, olrt: timedelta, y_of_x: Callable, xarg, yarg, xMRA, yMRA):
        raise NotImplementedError

    def cpf_crp_validate(self, env: Env, eut: Eut, dct_label: dict, df_meas, olrt: timedelta, y_of_x: Callable[[float], float]):
        raise NotImplementedError