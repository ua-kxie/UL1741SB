import numpy as np
from typing_extensions import Callable
from datetime import timedelta

from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.VoltReg import VoltReg


class VWCurve:
    '''IEEE 1547.1-2020 Tables 31-33'''
    def __init__(self, **kwargs):
        self.V1 = kwargs['V1']
        self.P1 = kwargs['P1']
        self.V2 = kwargs['V2']
        self.P2 = kwargs['P2']
        self.Tr = kwargs['Tr']

    def y_of_x(self, x):
        return np.interp(
            x,
            [self.V1, self.V2],
            [self.P1, self.P2],
        )

    @staticmethod
    def Crv_1A_inj(eut: Eut):
        """Create VW Curve 1A using Category A values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=10
        )

    @staticmethod
    def Crv_1A_abs(eut: Eut):
        """Create VW Curve 1A using Category A values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0,
            V2=1.1, P2=0, Tr=10
        )

    @staticmethod
    def Crv_1B_inj(eut: Eut):
        """Create VW Curve 1B using Category B values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=10
        )

    @staticmethod
    def Crv_1B_abs(eut: Eut):
        """Create VW Curve 1B using Category B values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0,
            V2=1.1, P2=0, Tr=10
        )

    @staticmethod
    def Crv_2A_inj(eut: Eut):
        """Create VW Curve 2A using Category A values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=60
        )

    @staticmethod
    def Crv_2A_abs(eut: Eut):
        """Create VW Curve 2A using Category A values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0,
            V2=1.1, P2=-1, Tr=60
        )

    @staticmethod
    def Crv_2B_inj(eut: Eut):
        """Create VW Curve 2B using Category B values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=60
        )

    @staticmethod
    def Crv_2B_abs(eut: Eut):
        """Create VW Curve 2B using Category B values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0,
            V2=1.1, P2=-1, Tr=60
        )

    @staticmethod
    def Crv_3A_inj(eut: Eut):
        """Create VW Curve 3A using Category A values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=0.5
        )

    @staticmethod
    def Crv_3A_abs(eut: Eut):
        """Create VW Curve 3A using Category A values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0,
            V2=1.1, P2=-1, Tr=0.5
        )

    @staticmethod
    def Crv_3B_inj(eut: Eut):
        """Create VW Curve 3B using Category B values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0,
            V2=1.1, P2=min(0.2, eut.Pmin / eut.Prated), Tr=0.5
        )

    @staticmethod
    def Crv_3B_abs(eut: Eut):
        """Create VW Curve 3B using Category B values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0,
            V2=1.1, P2=-1, Tr=0.5
        )

class VW(VoltReg):
    def vw_proc(self):
        """
        """
        if self.c_eut.Cat == self.c_eut.Category.A:
            vw_crvs = [
                ('1A_inj', VWCurve.Crv_1A_inj(self.c_eut)),
                ('2A_inj', VWCurve.Crv_2A_inj(self.c_eut)),
                ('3A_inj', VWCurve.Crv_3A_inj(self.c_eut)),
                ('1A_abs', VWCurve.Crv_1A_abs(self.c_eut)),
                ('2A_abs', VWCurve.Crv_2A_abs(self.c_eut)),
                ('3A_abs', VWCurve.Crv_3A_abs(self.c_eut))
            ]
        elif self.c_eut.Cat == self.c_eut.Category.B:
            vw_crvs = [
                ('1B_inj', VWCurve.Crv_1A_inj(self.c_eut)),
                ('2B_inj', VWCurve.Crv_2A_inj(self.c_eut)),
                ('3B_inj', VWCurve.Crv_3A_inj(self.c_eut)),
                ('1B_abs', VWCurve.Crv_1A_abs(self.c_eut)),
                ('2B_abs', VWCurve.Crv_2A_abs(self.c_eut)),
                ('3B_abs', VWCurve.Crv_3A_abs(self.c_eut))
            ]
        else:
            raise TypeError(f'unknown eut category {self.c_eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
        '''
        t) Repeat test steps d) through s) at EUT power set at 20% and 66% of rated power.
        '''
        for pwr_pu in [1, 0.2, 0.66]:
            '''
            u) Repeat steps d) through s) for Characteristics 2 and 3.
            '''
            self.c_eut.set_ap(Ena=True, pu=pwr_pu)
            if self.c_eut.Prated_prime == 0:
                # for euts incapable of absorption, do not test absorption curves
                vw_crvs = vw_crvs[:3]
            for crv_name, vw_crv in vw_crvs:
                '''
                v) Test may be repeated for EUTs that can also absorb power using the P’ values in the characteristic definition. 
                '''
                '''
                d) Adjust the EUT’s active power to Prated. For an EUT with an electrical input, set the input voltage to Vin_nom.
                e) Set EUT volt-watt parameters to the values specified by Characteristic 1. All other functions should be turned off.
                f) Verify volt-watt mode is reported as active and that the correct characteristic is reported.
                '''
                self.c_eut.set_vw(Ena=True, crv=vw_crv)
                for k, v in self.vw_traverse_steps(vw_crv).items():
                    dct_label = {'proc': 'vw', 'pwr': pwr_pu, 'crv': crv_name, 'step': k}
                    self.vw_validate(dct_label, lambda: self.c_env.ac_config(Vac=v), timedelta(seconds=vw_crv.Tr), lambda x: vw_crv.y_of_x(x / self.c_eut.VN) * self.c_eut.Prated)

    def vw_traverse_steps(self, vw_crv: VWCurve):
        """
        """
        '''
        g) Begin the adjustment towards VH. Step the ac test source voltage to av above VL.
        h) Step the ac test source voltage to av below V1
        i) Step the ac test source voltage to av above V1.
        j) Step the ac test source voltage to (V1 + V2)/2.
        k) Step the ac test source voltage to av below V2.
        l) Step the ac test source voltage to av above V2.
        m) Step the ac test source voltage to av below VH.
        n) Step the ac test source voltage to av above V2.
        o) Step the ac test source voltage to av below V2.
        p) Step the ac test source voltage to (V1 + V2)/2.
        q) Step the ac test source voltage to av above V1. 
        r) Step the ac test source voltage to av below V1.
        s) Step the ac test source voltage to av above VL.
        '''
        aV = self.c_eut.mra.static.V * 1.5
        ret = {
            'g': self.c_eut.VL + aV,
            'h': vw_crv.V1 * self.c_eut.VN - aV,
            'i': vw_crv.V1 * self.c_eut.VN + aV,
            'j': (vw_crv.V1 + vw_crv.V2) * self.c_eut.VN / 2.,
            'k': vw_crv.V2 * self.c_eut.VN - aV,
            'm': self.c_eut.VH - aV,
            'o': vw_crv.V2 * self.c_eut.VN - aV,
            'p': (vw_crv.V1 + vw_crv.V2) * self.c_eut.VN / 2.,
            'q': vw_crv.V1 * self.c_eut.VN + aV,
            'r': vw_crv.V1 * self.c_eut.VN - aV,
            's': self.c_eut.VL + aV
        }
        return ret

    def vw_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.9.3, +SB amendments
        Data from the test is used to confirm the manufacturer’s stated ratings. After each voltage or power step, a
        new steady-state active power, Pfinal, and steady-state voltage Vfinal is measured. To obtain a steady-state
        value, measurements shall be taken at a time period much larger than the open loop response, Tr, setting of
        the volt-watt function. As a guideline, at 2 times the open loop response time setting, the steady-state state
        error is 1%. In addition, instrumentation filtering may be used to reject any variation in ac test source
        voltage during steady-state measurement.

        After each voltage or power step, the open loop response time, Tr, is evaluated. The expected active power
        output, P(Tr), at one times the open loop response time, is calculated as 90% × (Pfinal – Pinitial) + Pinitial.
        Pfinal shall meet the test result accuracy requirements specified in 4.2 where Pfinal is the Y parameter and
        Vfinal is the X parameter.

        P(Tr) shall meet the test result accuracy requirements specified in 4.2 where P(Tr) is the Y parameter and Tr
        is the X parameter.

        SB amendments:
        The measured Pfinal shall be not more than P(Vfinal) + 1.5 * pMRA, where P(Vfinal) is the target power at 
        Vfinal calculated according to the piecewise linear characteristic under test. There is no tolerance on the 
        low side: Pfinal may be less than P(Vfinal) without limit.

        After each voltage or power step, the open loop response time Tr is evaluated. The measured active power output 
        P(tr) at olrt +/- 1.5 tMRA shall be not more than 0.9 * (Pfinal - Pinitial) + Pinitial + 1.5 * pMRA.
        '''
        xMRA = self.c_eut.mra.static.V
        yMRA = self.c_eut.mra.static.P
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'V', 'P'

        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, (xarg, yarg))

        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[1] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[1] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        '''
        P(tr) at olrt +/- 1.5 tMRA [...] shall be not more than 0.9 * (Pfinal - Pinitial) + Pinitial + 1.5 * pMRA
        '''
        y_thresh = y_init + 0.9 * (y_ss - y_init) + 1.5 * yMRA
        olrt_valid = y_olrt <= y_thresh

        '''
        Pfinal shall be not more than P(Vfinal) + 1.5 * pMRA
        '''
        # ss eval with 1741SB amendment
        y_targ = y_of_x(x_ss)
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_ss <= y_max
        df_meas['y_target'] = y_targ
        self.c_env.validate(dct_label={
            **dct_label,
            'y_init': y_init,
            'y_olrt': y_olrt,
            'y_ss': y_ss,
            'y_olrt_target': y_thresh,
            'y_ss_target': y_targ,
            'olrt_valid': olrt_valid,
            'ss_valid': ss_valid,
            'data': df_meas
        })
