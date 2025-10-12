"""
IEEE 1547.1-2020 5.16
"""
import pandas as pd

from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.RespPri import RespPri
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve

class RespPri1741(RespPri):
    """"""
    class PriTbl(RespPri.PriTbl):
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
            return RespPri1741.PriTbl(pd.DataFrame(data).set_index('step'))

    def pri_proc(self, env: Env, eut: Eut):
        """"""
        df_steps = self.PriTbl.catA() if eut.Cat == Eut.Category.A else self.PriTbl.catB()
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage and frequency trip parameters to the widest range of adjustability. Disable all
        reactive/active power control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        env.reset_to_nominal()
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
            eut.set_crp(Ena=True, pu=1)

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
            # TODO wait for ss
            eut.set_ap(Ena=True, pu=0.5)
            # TODO wait for ss
            # meas vac, fac, p, q
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
                env.ac_config(Vac=stepvals['vpu_ac'], Freq=stepvals['fhz_ac'])
                stepvals['e_ap_pu']  # expected active power
                stepvals[vars_key]  # expected reactive power
                raise NotImplementedError

    def pri_validation(self):
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
        # vv
        # crp
        # cpf
        # wv
