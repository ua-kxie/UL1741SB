"""
IEEE 1547.1-2020 5.5
"""

import numpy as np

from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env

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

class FreqDist:
    def of_trip_proc(self, env: Env, eut: Eut):
        '''
        '''
        shalltrip_tbl = eut.voltshalltrip_tbl
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source or signal injection generator parameters to the nominal operating conditions
        for the EUT.
        '''
        '''
        m) Repeat steps c) through l) for each overfrequency operating region.
        '''
        for op_region in [shalltrip_tbl.OF2, shalltrip_tbl.OF1]:
            '''
            c) Disable or program the relevant settings for all other active and reactive power control functions
            of the EUT to not influence the test results for the operating region being evaluated. Set the
            frequency droop function to the widest deadband setting and maximum droop setting to make the
            active power change with respect to frequency as small as possible.
            '''
            '''
            l) Set (or verify) the EUT parameters to the maximum overfrequency trip duration setting within the
            range of adjustment specified by the manufacturer and repeat steps f) through k).
            '''
            for trip_time in [op_region.cts_min, op_region.cts_max]:
                '''
                k) Set (or verify) EUT parameters at the maximum of the overfrequency trip magnitude setting
                within the range of adjustment specified by the manufacturer and repeat steps e) through j).
                '''
                for trip_mag in [op_region.hertz_min, op_region.hertz_max]:
                    '''
                    j) Repeat steps d) through i) four times for a total of five tests.
                    '''
                    for _ in range(5):
                        '''
                        d) Set (or verify) EUT parameters to the minimum [maximum] overfrequency trip magnitude setting within the
                        range of adjustment specified by the manufacturer.
                        e) Set (or verify) the EUT parameters to the minimum [maximum] overfrequency trip duration setting within the
                        range of adjustment specified by the manufacturer.
                        
                        f) Record applicable settings of the ac power source or signal injection generator and the EUT.
                        g) Adjust the ac test source frequency from PN to PB. The ac test source shall be held at this
                        frequency for period th.
                        h) At the end of this period, increase the frequency to PU and hold for a period not less than 1.5 times
                        the clearing time setting.
                        i) Record the frequency at which the unit trips and the clearing time.
                        '''
                        self.of_trip_validate()

    def of_trip_validate(self):
        """"""
        '''
        f) Record applicable settings of the ac power source or signal injection generator and the EUT.
        g) Adjust the ac test source frequency from PN to PB. The ac test source shall be held at this
        frequency for period th.
        h) At the end of this period, increase the frequency to PU and hold for a period not less than 1.5 times
        the clearing time setting.
        i) Record the frequency at which the unit trips and the clearing time.
        '''
        pass

    def hfrt_proc(self, env: Env, eut: Eut):
        """"""
        '''
        
        '''
        pass

"""HFRT"""
'''
a) Connect the EUT to a load bank according to manufacturer’s instructions.
b) Set or verify that the EUT is programmed using default settings.
c) Set the frequency droop function and droop values to make the active power change with respect to
frequency as small as possible.
d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
'''
'''
VFO CAPABLE:
e) Operate the EUT at nominal frequency ± 0.6 Hz35 into a load bank load capable of absorbing 100%
to 125% of the power rating of the EUT.

VFO INCAPABLE:
e) Operate the ac test source at nominal frequency ± 0.1 Hz.
'''
'''
f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
convenient power factor. Record the output current of the EUT at the nominal frequency condition.
'''
'''
VFO CAPABLE:
g) Adjust the EUT frequency from PN to PU where PU is greater than or equal to 61.8 Hz. The EUT
shall be held at this frequency or period th, which shall be not less than 299 s.
NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
capability of the EUT.
h) Decrease the frequency of the EUT to the nominal frequency ± 0.6 Hz.

VFO INCAPABLE:
g) Adjust the source frequency from PN to PU where fU is greater than or equal to 61.8 Hz. The source
shall be held at this frequency for period th, which shall be not less than 299 s.
NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
capability of the EUT.
h) Decrease the frequency of the ac test source to the nominal frequency ± 0.1 Hz.
'''
'''
i) Repeat steps f) and g) twice for a total of three tests.
j) During all frequency transitions in steps f) through h), the ROCOF shall be greater than or equal to
the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the demonstrated ROCOF
capability of the EUT.
'''

"""LFRT"""
'''
a) Connect the EUT to a load bank according to manufacturer’s instructions.
b) Set or verify that the EUT is programmed using default settings.
c) Set the frequency droop function and droop values to make the active power change with respect to
frequency as small as possible.
d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
'''
'''
VFO CAPABLE:
e) Operate the EUT at nominal frequency ± 0.6 Hz into a load bank load capable of absorbing 100%
to 125% of the power rating of the EUT.

VFO INCAPABLE:
e) Operate the ac test source at nominal frequency ± 0.1 Hz.
'''
'''
f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
convenient power factor. Record the output current of the EUT at the nominal frequency condition.
'''
'''
VFO CAPABLE:
g) Adjust the frequency of the EUT from PN to PU where PU is less than or equal to 57 Hz. The EUT
shall be held at this frequency for period th, which shall be not less than 299 s.
NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
capability of the EUT.
h) Increase the frequency of the EUT to the nominal frequency ± 0.6 Hz.

VFO INCAPABLE:
g) Adjust the frequency of the ac test source from PN to PU where PU is less than or equal to 57 Hz.
The source shall be held at this frequency for period th, which shall be not less than 299 s.
NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
capability of the EUT.
h) Increase the frequency of the ac test source to the nominal frequency ± 0.1 Hz.
'''
'''
i) Repeat steps f) and g) twice for a total of three tests. During all frequency transitions in steps f)
through h) the absolute ROCOF shall be greater than or equal to the ROCOF limit in Table 21 of
IEEE Std 1547-2018 and shall be within the demonstrated ROCOF capability of the EUT.
'''
