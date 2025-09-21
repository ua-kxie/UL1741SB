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
    def Crv_1A(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 1A using Category A values from Table 28"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.25 * Srated,  # absorption
            Q2=0,
            Q1=0,
            Q1_prime=0,
            Q2_prime=0,
            Q3_prime=0.44 * Srated  # injection
        )

    @staticmethod
    def Crv_1B(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 1B using Category B values from Table 28"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.44 * Srated,  # absorption
            Q2=0,
            Q1=0,
            Q1_prime=0,
            Q2_prime=0,
            Q3_prime=0.44 * Srated  # injection
        )

    @staticmethod
    def Crv_2A(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 2A using Category A values from Table 29"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.25 * Srated,  # absorption
            Q2=-0.13 * Srated,  # absorption
            Q1=-0.13 * Srated,  # absorption
            Q1_prime=0.22 * Srated,  # injection
            Q2_prime=0.22 * Srated,  # injection
            Q3_prime=0.44 * Srated  # injection
        )

    @staticmethod
    def Crv_2B(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 2B using Category B values from Table 29"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.44 * Srated,  # absorption
            Q2=-0.22 * Srated,  # absorption
            Q1=-0.22 * Srated,  # absorption
            Q1_prime=0.22 * Srated,  # injection
            Q2_prime=0.22 * Srated,  # injection
            Q3_prime=0.44 * Srated  # injection
        )

    @staticmethod
    def Crv_3A(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 3A using Category A values from Table 30"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.25 * Srated,  # absorption
            Q2=-0.25 * Srated,  # absorption
            Q1=0,
            Q1_prime=0,
            Q2_prime=0.44 * Srated,  # injection
            Q3_prime=0.44 * Srated  # injection
        )

    @staticmethod
    def Crv_3B(Prated, Pmin, Srated, Prated_prime, Pmin_prime):
        """Create WV Curve 3B using Category B values from Table 30"""
        return WVCurve(
            P3=Prated,
            P2=0.5 * Prated,
            P1=max(0.2 * Prated, Pmin),
            P1_prime=min(0.2 * Prated_prime, Pmin_prime),
            P2_prime=0.5 * Prated_prime,
            P3_prime=Prated_prime,
            Q3=-0.44 * Srated,  # absorption
            Q2=-0.44 * Srated,  # absorption
            Q1=0,
            Q1_prime=0,
            Q2_prime=0.44 * Srated,  # injection
            Q3_prime=0.44 * Srated  # injection
        )

class WV:
    def wv_traverse_steps(self, wv_crv: WVCurve, Pmin, Prated, aP, env: Env):
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
        ret = {
            'g': lambda: env.ac_config(Vac=Pmin),
            'h': lambda: env.ac_config(Vac=wv_crv.P1 - aP),
            'i': lambda: env.ac_config(Vac=wv_crv.P1 + aP),
            'j': lambda: env.ac_config(Vac=(wv_crv.P1 + wv_crv.P2) / 2.),
            'k': lambda: env.ac_config(Vac=wv_crv.P2 - aP),
            'l': lambda: env.ac_config(Vac=wv_crv.P2 + aP),
            'm': lambda: env.ac_config(Vac=(wv_crv.P2 + wv_crv.P3) / 2.),
            'n': lambda: env.ac_config(Vac=wv_crv.P3 - aP),
            'o': lambda: env.ac_config(Vac=wv_crv.P3 + aP),
            'p': lambda: env.ac_config(Vac=Prated),
            'q': lambda: env.ac_config(Vac=wv_crv.P3 + aP),
            'r': lambda: env.ac_config(Vac=wv_crv.P3 - aP),
            's': lambda: env.ac_config(Vac=(wv_crv.P2 + wv_crv.P3) / 2.),
            't': lambda: env.ac_config(Vac=wv_crv.P2 + aP),
            'u': lambda: env.ac_config(Vac=wv_crv.P2 - aP),
            'v': lambda: env.ac_config(Vac=(wv_crv.P1 + wv_crv.P2) / 2.),
            'w': lambda: env.ac_config(Vac=wv_crv.P1 + aP),
            'x': lambda: env.ac_config(Vac=wv_crv.P1 - aP),
            'y': lambda: env.ac_config(Vac=Pmin)
        }
        return ret

    def wv(self, env: Env, eut: Eut):
        """
        """
        env.log(msg="cpf proc against 1547")
        olrt = timedelta(seconds=10)
        VH, VN, VL, Pmin, Prated, multiphase = eut.VH, eut.VN, eut.VL, eut.Pmin, eut.Prated, eut.multiphase
        av = 1.5 * eut.mra.static.V
        if eut.Cat == Eut.Category.A:
            vv_crvs = [WVCurve.Crv_1A(eut.Prated, eut.VN)]  # just char1 curve, UL1741 amendment
        elif eut.Cat == Eut.Category.B:
            vv_crvs = [WVCurve.Crv_1B(eut.Prated, eut.VN)]
        else:
            raise TypeError(f'unknown eut category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source parameters to the nominal operating voltage and frequency.
        c) Set all EUT parameters to the rated active power conditions for the EUT.
        d) Set all voltage trip parameters to default settings.
        e) Set EUT watt-var parameters to the values specified by Characteristic 1. All other functions should
        be turned off.
        '''
        '''
        bb) Repeat steps f) through aa) for characteristics 2 and 3.
        '''
        for wv_crv in [WVCurve.Crv_1A(), WVCurve.Crv_2A(), WVCurve.Crv_3A()]:
            '''
            aa) Repeat test steps f) through z) at EUT power set at 20% and 66% of rated power.
            '''
            for pwr in [Prated, 0.2*Prated, 0.66*Prated]:
                '''
                z) If this EUT can absorb active power, repeat steps g) through y) using PN' values instead of PN.
                '''
                for Pnom in [PN, PN_prime]:
                    dct_vvsteps = self.wv_traverse_steps()