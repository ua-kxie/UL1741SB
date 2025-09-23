import numpy as np
from pyUL1741SB import Eut, Env

class VWCurve:
    '''IEEE 1547.1-2020 Tables 31-33'''
    def __init__(self, **kwargs):
        self.V1 = kwargs['V1']
        self.P1 = kwargs['P1']
        self.V2 = kwargs['V2']
        self.P2 = kwargs['P2']  # For DER that can only generate active power
        self.P2_prime = kwargs['P2_prime']  # For DER that can absorb active power
        self.Tr = kwargs['Tr']

    def y_of_x_inj(self, x):
        return np.interp(
            x,
            [self.V1, self.V2],
            [self.P1, self.P2],
        )

    def y_of_x_abs(self, x):
        return np.interp(
            x,
            [self.V1, self.V2],
            [self.P1, self.P2_prime],
        )

    @staticmethod
    def Crv_1A(Prated, Pmin):
        """Create VW Curve 1A using Category A values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=0, Tr=10
        )

    @staticmethod
    def Crv_1B(Prated, Pmin):
        """Create VW Curve 1B using Category B values from Table 31 (per-unit)"""
        return VWCurve(
            V1=1.06, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=0, Tr=10
        )

    @staticmethod
    def Crv_2A(Prated, Pmin, Prated_prime):
        """Create VW Curve 2A using Category A values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=-1, Tr=60
        )

    @staticmethod
    def Crv_2B(Prated, Pmin, Prated_prime):
        """Create VW Curve 2B using Category B values from Table 32 (per-unit)"""
        return VWCurve(
            V1=1.05, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=-1, Tr=60
        )

    @staticmethod
    def Crv_3A(Prated, Pmin, Prated_prime):
        """Create VW Curve 3A using Category A values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=-1, Tr=0.5
        )

    @staticmethod
    def Crv_3B(Prated, Pmin, Prated_prime):
        """Create VW Curve 3B using Category B values from Table 33 (per-unit)"""
        return VWCurve(
            V1=1.09, P1=1.0, V2=1.1,
            P2=min(0.2, Pmin / Prated), P2_prime=-1, Tr=0.5
        )

class VW:
    def vw_traverse_steps(self, env: Env, eut: Eut, vw_crv: VWCurve):
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
        aV = eut.mra.static.V * 1.5
        ret = {
            'g': lambda: env.ac_config(Vac=eut.VL + aV),
            'h': lambda: env.ac_config(Vac=vw_crv.V1 * eut.VN - aV),
            'i': lambda: env.ac_config(Vac=vw_crv.V1 * eut.VN + aV),
            'j': lambda: env.ac_config(Vac=(vw_crv.V1 + vw_crv.V2) * eut.VN / 2.),
            'k': lambda: env.ac_config(Vac=vw_crv.V2 * eut.VN - aV),
            'l': lambda: env.ac_config(Vac=vw_crv.V2 * eut.VN + aV),
            'm': lambda: env.ac_config(Vac=eut.VH - aV),
            'n': lambda: env.ac_config(Vac=vw_crv.V2 * eut.VN + aV),
            'o': lambda: env.ac_config(Vac=vw_crv.V2 * eut.VN - aV),
            'p': lambda: env.ac_config(Vac=(vw_crv.V1 + vw_crv.V2) * eut.VN / 2.),
            'q': lambda: env.ac_config(Vac=vw_crv.V1 * eut.VN + aV),
            'r': lambda: env.ac_config(Vac=vw_crv.V1 * eut.VN - aV),
            's': lambda: env.ac_config(Vac=eut.VL + aV)
        }
        return ret

    def vw_proc(self, env: Env, eut: Eut):
        """
        """
        if eut.Cat == Eut.Category.A:
            vw_crvs = [
                '1A', VWCurve.Crv_1A(eut.Prated, eut.Pmin),
                '2A', VWCurve.Crv_2A(eut.Prated, eut.Pmin, eut.Prated_prime),
                '3A', VWCurve.Crv_3A(eut.Prated, eut.Pmin, eut.Prated_prime)
            ]
        elif eut.Cat == Eut.Category.B:
            vw_crvs = [
                '1B', VWCurve.Crv_1A(eut.Prated, eut.Pmin),
                '2B', VWCurve.Crv_2A(eut.Prated, eut.Pmin, eut.Prated_prime),
                '3B', VWCurve.Crv_3A(eut.Prated, eut.Pmin, eut.Prated_prime)
            ]
        else:
            raise TypeError(f'unknown eut category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        '''
        t) Repeat test steps d) through s) at EUT power set at 20% and 66% of rated power.
        '''
        for pwr_pu in [1, 0.2, 0.66]:
            '''
            u) Repeat steps d) through s) for Characteristics 2 and 3.
            '''
            eut.active_power(Ena=True, pu=pwr_pu)
            for crv_name, vw_crv in vw_crvs:
                '''
                v) Test may be repeated for EUTs that can also absorb power using the P’ values in the characteristic definition. 
                '''
                '''
                d) Adjust the EUT’s active power to Prated. For an EUT with an electrical input, set the input voltage to Vin_nom.
                e) Set EUT volt-watt parameters to the values specified by Characteristic 1. All other functions should be turned off.
                f) Verify volt-watt mode is reported as active and that the correct characteristic is reported.
                '''
                lst_dct_steps = [self.vw_traverse_steps(env, eut, vw_crv)]
                if eut.Prated_prime < 0:
                    lst_dct_steps.append(self.vw_traverse_steps(env, eut, vw_crv))

    def vw_imbal(self):
        """
        """
        raise NotImplementedError
