import numpy as np

class VWCurve:
    '''IEEE 1547.1-2020 Tables 31-33'''
    def __init__(self, **kwargs):
        self.V1 = kwargs['V1']
        self.P1 = kwargs['P1']
        self.V2 = kwargs['V2']
        self.P2 = kwargs['P2']  # For DER that can only generate active power
        self.P2_prime = kwargs['P2_prime']  # For DER that can absorb active power
        self.Tr = kwargs['Tr']

    def y_of_x(self, x):
        return np.interp(
            x,
            [self.V1, self.V2],
            [self.P1, self.P2],
        )

    def y_of_x_ab(self, x):
        return np.interp(
            x,
            [self.V1, self.V2],
            [self.P1, self.P2_prime],
        )

    @staticmethod
    def Crv_1A(Prated, Pmin, VN):
        """Create VW Curve 1A using Category A values from Table 31"""
        return VWCurve(
            V1=1.06 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=0,  # For absorption-capable DER
            Tr=10
        )

    @staticmethod
    def Crv_1B(Prated, Pmin, VN):
        """Create VW Curve 1B using Category B values from Table 31"""
        return VWCurve(
            V1=1.06 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=0,  # For absorption-capable DER
            Tr=10
        )

    @staticmethod
    def Crv_2A(Prated, Pmin, Prated_prime, VN):
        """Create VW Curve 2A using Category A values from Table 32"""
        return VWCurve(
            V1=1.05 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=Prated_prime,  # For absorption-capable DER
            Tr=60  # 1741 amendment - IEEE 1547 stipulates 90, but is outside valid range
        )

    @staticmethod
    def Crv_2B(Prated, Pmin, Prated_prime, VN):
        """Create VW Curve 2B using Category B values from Table 32"""
        return VWCurve(
            V1=1.05 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=Prated_prime,  # For absorption-capable DER
            Tr=60  # 1741 amendment - IEEE 1547 stipulates 90, but is outside valid range
        )

    @staticmethod
    def Crv_3A(Prated, Pmin, Prated_prime, VN):
        """Create VW Curve 3A using Category A values from Table 33"""
        return VWCurve(
            V1=1.09 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=Prated_prime,  # For absorption-capable DER
            Tr=0.5
        )

    @staticmethod
    def Crv_3B(Prated, Pmin, Prated_prime, VN):
        """Create VW Curve 3B using Category B values from Table 33"""
        return VWCurve(
            V1=1.09 * VN,
            P1=Prated,
            V2=1.1 * VN,
            P2=min(0.2 * Prated, Pmin),  # For generation-only DER
            P2_prime=Prated_prime,  # For absorption-capable DER
            Tr=0.5
        )

def vw_traverse_steps(vw_crv: VWCurve, VL, VH, av):
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
    ret = {
        'g': lambda: grid.voltage(VL + av),
        'h': lambda: grid.voltage(vw_crv.V1 - av),
        'i': lambda: grid.voltage(vw_crv.V1 + av),
        'j': lambda: grid.voltage((vw_crv.V1 + vw_crv.V2) / 2.),
        'k': lambda: grid.voltage(vw_crv.V2 - av),
        'l': lambda: grid.voltage(vw_crv.V2 + av),
        'm': lambda: grid.voltage(VH - av),
        'n': lambda: grid.voltage(vw_crv.V2 + av),
        'o': lambda: grid.voltage(vw_crv.V2 - av),
        'p': lambda: grid.voltage((vw_crv.V1 + vw_crv.V2) / 2.),
        'q': lambda: grid.voltage(vw_crv.V1 + av),
        'r': lambda: grid.voltage(vw_crv.V1 - av),
        's': lambda: grid.voltage(VL + av)
    }
    return ret

def vw():
    """
    """
    '''
    a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
    b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power control functions.
    c) Set all ac test source parameters to the nominal operating voltage and frequency.
    '''
    '''
    t) Repeat test steps d) through s) at EUT power set at 20% and 66% of rated power.
    '''
    for pwr in [Prated, 0.2 * Prated, 0.66 * Prated]:
        '''
        u) Repeat steps d) through s) for Characteristics 2 and 3.
        '''
        for vw_crv in [VWCurve.Crv_1A(), VWCurve.Crv_2A(), VWCurve.Crv_3A()]:
            '''
            v) Test may be repeated for EUTs that can also absorb power using the P’ values in the characteristic definition. 
            '''
            # TODO unclear, not implemented in sandia's
            '''
            d) Adjust the EUT’s active power to Prated. For an EUT with an electrical input, set the input voltage to Vin_nom.
            e) Set EUT volt-watt parameters to the values specified by Characteristic 1. All other functions should be turned off.
            f) Verify volt-watt mode is reported as active and that the correct characteristic is reported.
            '''
            dct_steps = vw_traverse_steps()

def vw_imbal():
    """
    """
