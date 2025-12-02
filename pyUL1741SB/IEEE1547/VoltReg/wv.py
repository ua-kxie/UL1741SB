import numpy as np
from datetime import timedelta
from typing import Callable
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.VoltReg import VoltReg
from pyUL1741SB import viz


class WVCurve:
    '''IEEE 1547.1-2020 Tables 28-30'''

    def __init__(self, **kwargs):
        self.P3 = kwargs['P3']
        self.P2 = kwargs['P2']
        self.P1 = kwargs['P1']
        self.P1_prime = kwargs['P1_prime']
        self.P2_prime = kwargs['P2_prime']
        self.P3_prime = kwargs['P3_prime']
        self.Q3 = kwargs['Q3']
        self.Q2 = kwargs['Q2']
        self.Q1 = kwargs['Q1']
        self.Q1_prime = kwargs['Q1_prime']
        self.Q2_prime = kwargs['Q2_prime']
        self.Q3_prime = kwargs['Q3_prime']

    def y_of_x(self, x):
        return np.interp(
            x,
            [self.P3_prime, self.P2_prime, self.P1_prime, self.P1, self.P2, self.P3],
            [self.Q3_prime, self.Q2_prime, self.Q1_prime, self.Q1, self.Q2, self.Q3],
        )

    @staticmethod
    def Crv_1A(eut: Eut):
        """Create WV Curve 1A using Category A values from Table 28 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=0, Q1=0,
            Q1_prime=0, Q2_prime=0, Q3_prime=0.44
        )

    @staticmethod
    def Crv_1B(eut: Eut):
        """Create WV Curve 1B using Category B values from Table 28 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=0, Q1=0,
            Q1_prime=0, Q2_prime=0, Q3_prime=0.44
        )

    @staticmethod
    def Crv_2A(eut: Eut):
        """Create WV Curve 2A using Category A values from Table 29 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=-0.13, Q1=-0.13,
            Q1_prime=0.22, Q2_prime=0.22, Q3_prime=0.44
        )

    @staticmethod
    def Crv_2B(eut: Eut):
        """Create WV Curve 2B using Category B values from Table 29 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=-0.22, Q1=-0.22,
            Q1_prime=0.22, Q2_prime=0.22, Q3_prime=0.44
        )

    @staticmethod
    def Crv_3A(eut: Eut):
        """Create WV Curve 3A using Category A values from Table 30 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=-0.25, Q1=0,
            Q1_prime=0, Q2_prime=0.44, Q3_prime=0.44
        )

    @staticmethod
    def Crv_3B(eut: Eut):
        """Create WV Curve 3B using Category B values from Table 30 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(
            -0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=-0.44, Q1=0,
            Q1_prime=0, Q2_prime=0.44, Q3_prime=0.44
        )


proc = 'wv'


class WV(VoltReg):
    def wv(self, outdir, final):
        self.validator = viz.Validator(proc)
        try:
            self.wv_proc()
            final()
        finally:
            self.validator.draw_new(outdir)

    def wv_proc(self):
        """
        """
        self.c_env.log(msg="wv proc against 1547")
        olrt = timedelta(seconds=self.c_eut.olrt.wv)
        if self.c_eut.Cat == self.c_eut.Category.A:
            wv_crvs = [
                ('1A', WVCurve.Crv_1A(self.c_eut)),
                ('2A', WVCurve.Crv_2A(self.c_eut)),
                ('3A', WVCurve.Crv_3A(self.c_eut)),
            ]
        elif self.c_eut.Cat == self.c_eut.Category.B:
            wv_crvs = [
                ('1B', WVCurve.Crv_1B(self.c_eut)),
                ('2B', WVCurve.Crv_2B(self.c_eut)),
                ('3B', WVCurve.Crv_3B(self.c_eut)),
            ]
        else:
            raise TypeError(f'unknown eut category {self.c_eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source parameters to the nominal operating voltage and frequency.
        c) Set all EUT parameters to the rated active power conditions for the self.c_eut.
        d) Set all voltage trip parameters to default settings.
        e) Set EUT watt-var parameters to the values specified by Characteristic 1. All other functions should
        be turned off.
        '''
        self.conn_to_grid()
        self.default_cfg()
        self.c_env.ac_config(
            Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        vttbl = self.c_eut.voltshalltrip_tbl
        self.c_eut.set_vt(**{
            'OV1': {'cts': vttbl.OV1.cts, 'vpu': vttbl.OV1.volt_pu},
            'OV2': {'cts': vttbl.OV2.cts, 'vpu': vttbl.OV2.volt_pu},
            'UV1': {'cts': vttbl.UV1.cts, 'vpu': vttbl.UV1.volt_pu},
            'UV2': {'cts': vttbl.UV2.cts, 'vpu': vttbl.UV2.volt_pu},
        })
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False, autoVrefEna=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
        '''
        bb) Repeat steps f) through aa) for characteristics 2 and 3.
        '''
        for crv_key, wv_crv in wv_crvs:
            self.c_eut.set_wv(Ena=True, crv=wv_crv)
            lst_dct_steps = [('inj', self.wv_traverse_steps_inj(wv_crv))]
            '''
            z) If this EUT can absorb active power, repeat steps g) through y) using PN' values instead of PN.
            '''
            if self.c_eut.Prated_prime < 0:
                lst_dct_steps.append(
                    ('abs', self.wv_traverse_steps_abs(wv_crv)))

            # validate for all steps
            for direction, dct_steps in lst_dct_steps:
                for k, step in dct_steps.items():
                    dct_label = {'proc': 'wv', 'crv': crv_key,
                                 'dir': direction, 'step': k}
                    self.wv_step_validate(
                        dct_label,
                        lambda: self.c_eut.set_aap(spu=max(min(step, 1), -1)),
                        olrt,
                        lambda x: wv_crv.y_of_x(x / self.c_eut.Prated) * self.c_eut.Prated
                    )

    def wv_traverse_steps_inj(self, wv_crv: WVCurve):
        """
        """
        '''
        f) Record applicable settings.
        g) Set the EUT’s available active power to Pmin.
        h) Begin the adjustment to Prated. Step the EUT’s available active power to aP below P1.
        i) Step the EUT’s available active power to aP above P1.
        j) Step the EUT’s available active power to (P1 + P2)/2.
        k) Step the EUT’s available active power to aP below P2.
        l) Step the EUT’s available active power to aP above P2.
        m) Step the EUT’s available active power to (P2 + P3)/2.
        n) Step the EUT’s available active power to aP below P3. 
        o) Step the EUT’s available active power to aP above P3.
        p) Step the EUT’s available active power to Prated.
        q) Begin the return to Pmin. Step the EUT power to aP above P3.
        r) Step the EUT’s available active power to aP below P3.
        s) Step the EUT’s available active power to (P2 + P3)/2.
        t) Step the EUT’s available active power to aP above P2.
        u) Step the EUT’s available active power to aP below P2.
        v) Step the EUT’s available active power to (P1 + P2)/2.
        w) Step the EUT’s available active power to aP above P1.
        x) Step the EUT’s available active power to aP below P1.
        y) Step the EUT’s available active power to Pmin.
        '''
        aP = self.mra_scale * self.c_eut.mra.static.P / self.c_eut.Prated
        ret = {
            'g': self.c_eut.Pmin / self.c_eut.Prated,
            'h': wv_crv.P1 - aP,
            'i': wv_crv.P1 + aP,
            'j': (wv_crv.P1 + wv_crv.P2) / 2.,
            'k': wv_crv.P2 - aP,
            'l': wv_crv.P2 + aP,
            'm': (wv_crv.P2 + wv_crv.P3) / 2.,
            'n': wv_crv.P3 - aP,
            'o': wv_crv.P3 + aP,
            'p': 1,
            'q': wv_crv.P3 + aP,
            'r': wv_crv.P3 - aP,
            's': (wv_crv.P2 + wv_crv.P3) / 2.,
            't': wv_crv.P2 + aP,
            'u': wv_crv.P2 - aP,
            'v': (wv_crv.P1 + wv_crv.P2) / 2.,
            'w': wv_crv.P1 + aP,
            'x': wv_crv.P1 - aP,
            'y': self.c_eut.Pmin / self.c_eut.Prated
        }
        return ret

    def wv_traverse_steps_abs(self, wv_crv: WVCurve):
        """
        """
        aP = self.mra_scale * self.c_eut.mra.static.P / self.c_eut.Prated
        ret = {
            'g': self.c_eut.Pmin_prime / self.c_eut.Prated,
            'h': wv_crv.P1_prime + aP,
            'i': wv_crv.P1_prime - aP,
            'j': (wv_crv.P1_prime + wv_crv.P2_prime) / 2.,
            'k': wv_crv.P2_prime + aP,
            'l': wv_crv.P2_prime - aP,
            'm': (wv_crv.P2_prime + wv_crv.P3_prime) / 2.,
            'n': wv_crv.P3_prime + aP,
            'o': wv_crv.P3_prime - aP,
            'p': -1,
            'q': wv_crv.P3_prime - aP,
            'r': wv_crv.P3_prime + aP,
            's': (wv_crv.P2_prime + wv_crv.P3_prime) / 2.,
            't': wv_crv.P2_prime - aP,
            'u': wv_crv.P2_prime + aP,
            'v': (wv_crv.P1_prime + wv_crv.P2_prime) / 2.,
            'w': wv_crv.P1_prime - aP,
            'x': wv_crv.P1_prime + aP,
            'y': self.c_eut.Pmin_prime / self.c_eut.Prated
        }
        return ret

    def wv_step_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        xMRA = self.c_eut.mra.static.P
        yMRA = self.c_eut.mra.static.Q
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'P', 'Q'

        self.vv_wv_step_validate(
            dct_label, perturb, xarg, yarg, y_of_x, olrt, xMRA, yMRA)
