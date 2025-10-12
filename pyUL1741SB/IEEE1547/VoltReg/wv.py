import numpy as np
from datetime import timedelta

from pyUL1741SB import Eut, Env

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
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=0, Q1=0,
            Q1_prime=0, Q2_prime=0, Q3_prime=0.44
        )

    @staticmethod
    def Crv_1B(eut: Eut):
        """Create WV Curve 1B using Category B values from Table 28 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=0, Q1=0,
            Q1_prime=0, Q2_prime=0, Q3_prime=0.44
        )

    @staticmethod
    def Crv_2A(eut: Eut):
        """Create WV Curve 2A using Category A values from Table 29 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=-0.13, Q1=-0.13,
            Q1_prime=0.22, Q2_prime=0.22, Q3_prime=0.44
        )

    @staticmethod
    def Crv_2B(eut: Eut):
        """Create WV Curve 2B using Category B values from Table 29 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=-0.22, Q1=-0.22,
            Q1_prime=0.22, Q2_prime=0.22, Q3_prime=0.44
        )

    @staticmethod
    def Crv_3A(eut: Eut):
        """Create WV Curve 3A using Category A values from Table 30 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.25, Q2=-0.25, Q1=0,
            Q1_prime=0, Q2_prime=0.44, Q3_prime=0.44
        )

    @staticmethod
    def Crv_3B(eut: Eut):
        """Create WV Curve 3B using Category B values from Table 30 (per unit)"""
        P1_prime = 0 if eut.Prated_prime == 0 else min(-0.2, -eut.Pmin_prime / eut.Prated_prime)
        return WVCurve(
            P3=1.0, P2=0.5, P1=max(0.2, eut.Pmin / eut.Prated),
            P1_prime=P1_prime, P2_prime=-0.5, P3_prime=-1.0,
            Q3=-0.44, Q2=-0.44, Q1=0,
            Q1_prime=0, Q2_prime=0.44, Q3_prime=0.44
        )

class WV:
    def wv_traverse_steps_inj(self, env: Env, eut: Eut, wv_crv: WVCurve):
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
        aP = 1.5 * eut.mra.static.P / eut.Prated
        step_keys = ['g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y']
        pwrs_inj = [
            eut.Pmin/eut.Prated,
            wv_crv.P1 - aP,
            wv_crv.P1 + aP,
            (wv_crv.P1 + wv_crv.P2) / 2.,
            wv_crv.P2 - aP,
            wv_crv.P2 + aP,
            (wv_crv.P2 + wv_crv.P3) / 2.,
            wv_crv.P3 - aP,
            wv_crv.P3 + aP,
            1,
            wv_crv.P3 + aP,
            wv_crv.P3 - aP,
            (wv_crv.P2 + wv_crv.P3) / 2.,
            wv_crv.P2 + aP,
            wv_crv.P2 - aP,
            (wv_crv.P1 + wv_crv.P2) / 2.,
            wv_crv.P1 + aP,
            wv_crv.P1 - aP,
            eut.Pmin/eut.Prated,
        ]
        ret = {k: v for k, v in zip(step_keys, pwrs_inj)}
        return ret

    def wv_traverse_steps_abs(self, env: Env, eut: Eut, wv_crv: WVCurve):
        """
        """
        aP = 1.5 * eut.mra.static.P / eut.Prated
        step_keys = ['g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y']
        pwrs_abs = [
            eut.Pmin_prime/eut.Prated,
            wv_crv.P1_prime + aP,
            wv_crv.P1_prime - aP,
            (wv_crv.P1_prime + wv_crv.P2_prime) / 2.,
            wv_crv.P2_prime + aP,
            wv_crv.P2_prime - aP,
            (wv_crv.P2_prime + wv_crv.P3_prime) / 2.,
            wv_crv.P3_prime + aP,
            wv_crv.P3_prime - aP,
            -1,
            wv_crv.P3_prime - aP,
            wv_crv.P3_prime + aP,
            (wv_crv.P2_prime + wv_crv.P3_prime) / 2.,
            wv_crv.P2_prime - aP,
            wv_crv.P2_prime + aP,
            (wv_crv.P1_prime + wv_crv.P2_prime) / 2.,
            wv_crv.P1_prime - aP,
            wv_crv.P1_prime + aP,
            eut.Pmin_prime/eut.Prated,
        ]
        ret = {k: v for k, v in zip(step_keys, pwrs_abs)}
        return ret

    def wv_proc(self, env: Env, eut: Eut):
        """
        """
        raise NotImplementedError
