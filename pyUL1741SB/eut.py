import enum
import numpy as np

class VoltShallTripValue:
    def __init__(self, volt, cts, volt_min=None, volt_max=None, cts_min=None, cts_max=None):
        self.__volt_pu = volt
        self.__cts = cts
        self.__volt_min = volt if volt_min is None else volt_min
        self.__volt_max = volt if volt_max is None else volt_max
        self.__cts_min = cts if cts_min is None else cts_min
        self.__cts_max = cts if cts_max is None else cts_max

    @property
    def volt_pu(self):
        return self.__volt_pu
    @volt_pu.setter
    def volt_pu(self, value):
        self.__volt_pu = np.clip(value, self.__volt_min, self.__volt_max)

    @property
    def cts(self):
        return self.__cts
    @cts.setter
    def cts(self, value):
        self.__cts = np.clip(value, self.__cts_min, self.__cts_max)

    @property
    def volt_pu_min(self):
        return self.__volt_min
    @property
    def volt_pu_max(self):
        return self.__volt_max
    @property
    def cts_min(self):
        return self.__cts_min
    @property
    def cts_max(self):
        return self.__cts_max

class VoltShallTripTable:
    def __init__(self, ov2: VoltShallTripValue, ov1: VoltShallTripValue, uv1: VoltShallTripValue, uv2: VoltShallTripValue):
        self.OV2 = ov2
        self.OV1 = ov1
        self.UV1 = uv1
        self.UV2 = uv2

    @staticmethod
    def AOPCatI(VN: float):
        '''
        IEEE 1547-2018 Table 11
        '''
        return VoltShallTripTable(
            VoltShallTripValue(1.20 , 0.16),  # OV2: fixed values
            VoltShallTripValue(1.10 , 2.0, 1.10 , 1.20 , 1.0, 13.0),  # OV1
            VoltShallTripValue(0.70 , 2.0, 0.0 , 0.88 , 2.0, 21.0),  # UV1
            VoltShallTripValue(0.45 , 0.16, 0.0 , 0.50 , 0.16, 2.0)   # UV2
        )

    @staticmethod
    def AOPCatII(VN: float):
        '''
        IEEE 1547-2018 Table 12
        '''
        return VoltShallTripTable(
            VoltShallTripValue( 1.20, 0.16),  # OV2: fixed values
            VoltShallTripValue( 1.10, 2.0,  1.10,  1.20, 1.0, 13.0),  # OV1
            VoltShallTripValue( 0.70, 10.0,  0.0,  0.88, 2.0, 21.0),  # UV1 (different default time)
            VoltShallTripValue( 0.45, 0.16,  0.0,  0.50, 0.16, 2.0)   # UV2
        )

    @staticmethod
    def AOPCatIII(VN: float):
        '''
        IEEE 1547-2018 Table 13
        '''
        return VoltShallTripTable(
            VoltShallTripValue( 1.20, 0.16),  # OV2: fixed values
            VoltShallTripValue( 1.10, 13.0, 1.10, 1.20, 1.0, 13.0),  # OV1 (different default time)
            VoltShallTripValue( 0.88, 21.0, 0.0, 0.88, 21.0, 50.0),  # UV1 (different values)
            VoltShallTripValue( 0.50, 2.0, 0.0, 0.50, 2.0, 21.0)    # UV2 (different values)
        )

class FreqShallTripValue:
    def __init__(self, hertz, cts, hertz_min=None, hertz_max=None, cts_min=None, cts_max=None):
        self.__hertz = hertz
        self.__cts = cts
        self.__hertz_min = hertz if hertz_min is None else hertz_min
        self.__hertz_max = hertz if hertz_max is None else hertz_max
        self.__cts_min = cts if cts_min is None else cts_min
        self.__cts_max = cts if cts_max is None else cts_max

    @property
    def hertz(self):
        return self.__hertz
    @hertz.setter
    def hertz(self, value):
        self.__hertz = np.clip(value, self.__hertz_min, self.__hertz_max)

    @property
    def cts(self):
        return self.__cts
    @cts.setter
    def cts(self, value):
        self.__cts = np.clip(value, self.__cts_min, self.__cts_max)

    @property
    def volt_pu_min(self):
        return self.__hertz_min
    @property
    def volt_pu_max(self):
        return self.__hertz_max
    @property
    def cts_min(self):
        return self.__cts_min
    @property
    def cts_max(self):
        return self.__cts_max
    @property
    def hertz_min(self):
        return self.__hertz_min
    @property
    def hertz_max(self):
        return self.__hertz_max

class FreqShallTripTable:
    def __init__(self, of2: FreqShallTripValue, of1: FreqShallTripValue, uf1: FreqShallTripValue, uf2: FreqShallTripValue):
        self.OF2 = of2
        self.OF1 = of1
        self.UF1 = uf1
        self.UF2 = uf2

    @staticmethod
    def MaxRange():
        """"""
        '''
        IEEE 1547-2018 Table 18
        '''
        return FreqShallTripTable(
            FreqShallTripValue(62, 0.16, 61.8, 66, 0.16, 1e3),
            FreqShallTripValue(61.2, 300, 61.0, 66, 180, 1e3),
            FreqShallTripValue(58.5, 300, 50, 59, 180, 1e3),
            FreqShallTripValue(56.5, 0.16, 50, 57, 0.16, 1e3),
        )

"""
IEEE 1547-2018 Table 21 
Rate of Change of Frequency (ROCOF) Ride-Through Requirements
for DER of Abnormal Operating Performance Categories I, II, and III

+-----------+-----------+-----------+
| Category I| Category II| Category III|
+-----------+-----------+-----------+
|  0.5 Hz/s |  2.0 Hz/s |  3.0 Hz/s |
+-----------+-----------+-----------+
"""

class Eut:
    class State(enum.Enum):
        """
        der state
        """
        OFF = 1
        SLEEPING = 2
        STARTING = 3
        RUNNING = 4
        THROTTLED = 5
        SHUTTING_DOWN = 6
        FAULT = 7
        STANDBY = 8
    class AOPCat(enum.Enum):
        """
        abnormal performance category
        """
        I = 1
        II = 2
        III = 3
    class Category(enum.Enum):
        A = 1
        B = 2
    class Comms(enum.Enum):
        SEP2 = 0
        DNP3 = 1
        SUNS = 2
    class MRA:
        '''
        Minimum required accuracy (MRA) (per Table 3 of IEEE Std 1547-2018)

        Table 3 - Minimum measurement and calculation accuracy requirements for manufacturers
        ______________________________________________________________________________________________
        Time frame                  Steady-state measurements
        Parameter       Minimum measurement accuracy    Measurement window      Range
        ______________________________________________________________________________________________
        Voltage, RMS    (+/- 1% Vnom)                   10 cycles               0.5 p.u. to 1.2 p.u.
        Frequency       10 mHz                          60 cycles               50 Hz to 66 Hz
        Active Power    (+/- 5% Srated)                 10 cycles               0.2 p.u. < P < 1.0
        Reactive Power  (+/- 5% Srated)                 10 cycles               0.2 p.u. < Q < 1.0
        Time            1% of measured duration         N/A                     5 s to 600 s
        ______________________________________________________________________________________________
                                    Transient measurements
        Parameter       Minimum measurement accuracy    Measurement window      Range
        Voltage, RMS    (+/- 2% Vnom)                   5 cycles                0.5 p.u. to 1.2 p.u.
        Frequency       100 mHz                         5 cycles                50 Hz to 66 Hz
        Time            2 cycles                        N/A                     100 ms < 5 s
        ______________________________________________________________________________________________
        '''

        class Static:
            def __init__(self, v_nominal, s_rated):
                self.V = 0.01 * v_nominal
                self.F = 0.01
                self.P = 0.05 * s_rated
                self.Q = 0.05 * s_rated
                self.__T = 0.01  # 1 % of measured duration

            def T(self, dur_s: float):
                return self.__T * max(5, min(dur_s, 600))

        class Dynamic:
            def __init__(self, v_nominal):
                self.V = 0.02 * v_nominal
                self.F = 0.1
                self.T = 2. / 60.

        def __init__(self, v_nominal, s_rated):
            self.static = self.Static(v_nominal, s_rated)
            self.dynamic = self.Dynamic(v_nominal)
    def __init__(self, **kwargs):
        # general params
        k, t = 'Cat', self.Category
        if isinstance(kwargs[k], t):
            self.Cat = kwargs[k]
        else:
            raise TypeError(f"{k} must be of type {t.__name__}.")

        k, t = 'aopCat', self.AOPCat
        if isinstance(kwargs[k], t):
            self.aopCat = kwargs[k]
        else:
            raise TypeError(f"{k} must be of type {t.__name__}.")

        k, t = 'voltshalltrip_tbl', VoltShallTripTable
        if isinstance(kwargs[k], t):
            self.voltshalltrip_tbl = kwargs[k]
        else:
            raise TypeError(f"{k} must be of type {t.__name__}.")

        k, t = 'freqshalltrip_tbl', FreqShallTripTable
        if isinstance(kwargs[k], t):
            self.freqshalltrip_tbl = kwargs[k]
        else:
            raise TypeError(f"{k} must be of type {t.__name__}.")
        self.vfo = kwargs['vfo']  # variable frequency output capable (see frt tests)
        self.Comms = kwargs['Comms']  # comms protocols to test - sunspec, dnp3, I3E 2030.5
        self.multiphase = kwargs['multiphase']  # comms protocols to test - sunspec, dnp3, I3E 2030.5
        self.Prated = kwargs['Prated']  # output power rating (W)
        self.Prated_prime = kwargs['Prated_prime']  # for EUTs that can sink power, output power rating while sinking power (W)
        self.Srated = kwargs['Srated']  # apparent power rating (VA)
        # Volt Reg params
        self.Vin_nom = kwargs['Vin_nom']  # for an EUT with an electrical input, nominal input voltage (V)
        self.Vin_min = kwargs['Vin_min']  # for an EUT with an electrical input, minimum input voltage (V)
        self.Vin_max = kwargs['Vin_max']  # for an EUT with an electrical input, maximum input voltage (V)
        self.VN = kwargs['VN']  # nominal output voltage (V)
        self.VL = kwargs['VL']  # minimum output voltage in the continuous operating region (V)
        self.VH = kwargs['VH']  # maximum output voltage in the continuous operating region (V)
        self.Pmin = kwargs['Pmin']  # minimum active power (W)
        self.Pmin_prime = kwargs['Pmin_prime']  # for EUTs that can sink power, minimum active power while sinking power (W)
        self.Qrated_abs = kwargs['Qrated_abs']  # maximum absorbed reactive power (var)
        self.Qrated_inj = kwargs['Qrated_inj']  # minimum injected reactive power (var)
        self.Qrated_inj = kwargs['Qrated_inj']  # minimum injected reactive power (var)
        # Freq Reg params
        self.fL = kwargs['fL']
        self.fN = kwargs['fN']
        self.fH = kwargs['fH']
        self.delta_Psmall = kwargs['delta_Psmall']
        self.delta_Plarge = kwargs['delta_Plarge']
        # post
        self.mra = self.MRA(self.VN, self.Prated)

    def rocof(self):
        """
        IEEE 1547.1-2018 6.5.2.5
        returns rocof in hz/s
        """
        return {
            Eut.AOPCat.I: 0.5,
            Eut.AOPCat.II: 2.0,
            Eut.AOPCat.III: 3.0,
        }[self.aopCat]

    def reactive_power(self, **kwargs):
        if len(kwargs) == 0:
            # treat as query
            return {'Ena': False}
        pass

    def active_power(self, **kwargs):
        if len(kwargs) == 0:
            # treat as query
            return {'Ena': False}
        pass

    def fixed_pf(self, **kwargs):
        pass

    def state(self):
        pass

    def vv(self, **kwargs):
        pass

    def set_vt(self, **kwargs):
        pass

    def set_ft(self, **kwargs):
        pass
