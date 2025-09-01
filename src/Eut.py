import enum

class Eut:
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
                self.T = 0.01

        class Dynamic:
            def __init__(self, v_nominal):
                self.V = 0.02 * v_nominal
                self.F = 0.1
                self.T = 2. / 60.

        def __init__(self, v_nominal, s_rated):
            self.static = self.Static(v_nominal, s_rated)
            self.dynamic = self.Dynamic(v_nominal)
    def __init__(self, **kwargs):
        if type(kwargs['Cat']) is self.Category:
            self.Cat = kwargs['Cat']
        else:
            raise TypeError("'Cat' must be of type Category.")
        self.Prated = kwargs['Prated']  # output power rating (W)
        self.Prated_prime = kwargs['Prated_prime']  # for EUTs that can sink power, output power rating while sinking power (W)
        self.Srated = kwargs['Srated']  # apparent power rating (VA)
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
        self.Comms = kwargs['Comms']  # comms protocols to test - sunspec, dnp3, I3E 2030.5
        self.multiphase = kwargs['multiphase']  # comms protocols to test - sunspec, dnp3, I3E 2030.5
        self.mra = self.MRA(self.VN, self.Prated)

    def reactive_power(self, **kwargs):
        pass

    def active_power(self, **kwargs):
        pass

    def fixed_pf(self, **kwargs):
        pass