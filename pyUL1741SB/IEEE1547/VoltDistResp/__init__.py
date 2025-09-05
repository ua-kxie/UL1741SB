'''
5.4 Test for response to voltage disturbances
'''

from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env
import numpy as np

class VoltShallTripValue:
    def __init__(self, volt_pu, cts, volt_pu_min=None, volt_pu_max=None, cts_min=None, cts_max=None):
        self.__volt_pu = volt_pu
        self.__cts = cts
        self.__volt_pu_min = volt_pu if volt_pu_min is None else volt_pu_min
        self.__volt_pu_max = volt_pu if volt_pu_max is None else volt_pu_max
        self.__cts_min = cts if cts_min is None else cts_min
        self.__cts_max = cts if cts_max is None else cts_max

    @property
    def volt_pu(self):
        return self.__volt_pu
    @volt_pu.setter
    def volt_pu(self, value):
        self.__volt_pu = np.clip(value, self.__volt_pu_min, self.__volt_pu_max)

    @property
    def cts(self):
        return self.__cts
    @cts.setter
    def cts(self, value):
        self.__cts = np.clip(value, self.__cts_min, self.__cts_max)

    @property
    def volt_pu_min(self):
        return self.__volt_pu_min
    @property
    def volt_pu_max(self):
        return self.__volt_pu_max
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
    def AOPCatI():
        '''
        IEEE 1547-2018 Table 11
        '''
        return VoltShallTripTable(
            VoltShallTripValue(1.20, 0.16),  # OV2: fixed values
            VoltShallTripValue(1.10, 2.0, 1.10, 1.20, 1.0, 13.0),  # OV1
            VoltShallTripValue(0.70, 2.0, 0.0, 0.88, 2.0, 21.0),  # UV1
            VoltShallTripValue(0.45, 0.16, 0.0, 0.50, 0.16, 2.0)   # UV2
        )

    @staticmethod
    def AOPCatII():
        '''
        IEEE 1547-2018 Table 12
        '''
        return VoltShallTripTable(
            VoltShallTripValue(1.20, 0.16),  # OV2: fixed values
            VoltShallTripValue(1.10, 2.0, 1.10, 1.20, 1.0, 13.0),  # OV1
            VoltShallTripValue(0.70, 10.0, 0.0, 0.88, 2.0, 21.0),  # UV1 (different default time)
            VoltShallTripValue(0.45, 0.16, 0.0, 0.50, 0.16, 2.0)   # UV2
        )

    @staticmethod
    def AOPCatIII():
        '''
        IEEE 1547-2018 Table 13
        '''
        return VoltShallTripTable(
            VoltShallTripValue(1.20, 0.16),  # OV2: fixed values
            VoltShallTripValue(1.10, 13.0, 1.10, 1.20, 1.0, 13.0),  # OV1 (different default time)
            VoltShallTripValue(0.88, 21.0, 0.0, 0.88, 21.0, 50.0),  # UV1 (different values)
            VoltShallTripValue(0.50, 2.0, 0.0, 0.50, 2.0, 21.0)    # UV2 (different values)
        )

class VoltDist:
    def ov_trip_proc(self, env: Env, eut: Eut):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError
        shalltrip_tbl = eut.voltshalltrip_tbl
        VN = eut.VN
        vMRA = eut.mra.static.V
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the EUT.
        '''
        '''
        k) Repeat steps c) through k) for each overvoltage operating trip region.
        '''
        for trip_region in [shalltrip_tbl.OV2, shalltrip_tbl.OV1]:
            '''
            c) Set (or verify) all EUT parameters to the nominal operating settings. If the overvoltage setting is
            adjustable, set the EUT to the minimum overvoltage setting, but no less than the nominal voltage
            plus twice the minimum required accuracy for voltage.
            d) Set the trip time setting to the minimum.
            '''
            '''
            i) If the trip magnitude is adjustable, repeat steps e) through h) at the [minimum] maximum of the range.
            '''
            trip_mags = [trip_region.volt_pu_min, trip_region.volt_pu_max]
            for trip_mag in trip_mags:
                trip_mag = max(trip_mag, VN + 2 * vMRA)
                '''
                j) Set the trip time setting to the maximum and repeat steps e) through i).
                '''
                trip_times = [trip_region.cts_min, trip_region.cts_max]
                for trip_time in trip_times:
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    '''
                    h) For multiphase units, repeat steps e) through g) for the applicable voltage on each phase or phase
                    pair individually, and all phases simultaneously.
                    '''
                    for _ in range(5):
                        '''
                        e) Record applicable settings.
                        For single-phase units, adjust the applicable voltage to parameter starting point Pb, as defined in
                        A.3, to a value greater than or equal to the setpoint value determined in step c) minus 200% of
                        the MRA. The source shall be held at this voltage for a period th.
                        At the end of this period, initiate a step of the voltage to a level less than or equal to the setpoint
                        value plus 200% of the MRA using the procedure specified in A.3. For multiphase units,
                        adjust voltage on one phase using the values above. Verify that remaining phases are held at
                        nominal ±0.02 p.u.
                        f) Record all voltage magnitudes when the unit trips.
                        '''
                        pass

    def ov_trip_validate(self, env:Env, t_set, v_init, v_set, tMRA, vMRA):
        """"""
        '''
        For single-phase units, adjust the applicable voltage to parameter starting point Pb, as defined in
        A.3, to a value greater than or equal to the setpoint value determined in step c) minus 200% of
        the MRA. The source shall be held at this voltage for a period th. 
        The variable th is at 100% of the trip time setting plus 200% MRA
        At the end of this period, initiate a step of the voltage to a level less than or equal to the setpoint
        value plus 200% of the MRA using the procedure specified in A.3. For multiphase units,
        adjust voltage on one phase using the values above. Verify that remaining phases are held at
        nominal ±0.02 p.u.
        Record all voltage magnitudes when the unit trips.
        
        5.4.3.4 Criteria
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within the
        respective clearing times for each undervoltage tripping range specified in IEEE Std 1547. The evaluated
        ranges of adjustment for tripping magnitude and duration shall be greater than or equal to the allowable
        ranges of adjustment for each undervoltage tripping range specified in IEEE Std 1547.
        '''
        env.ac_config(Vac=v_init + 2 * vMRA)
        env.sleep(t_set + 2 * tMRA)
        env.ac_config(Vac=v_set + 2 * vMRA)
        # don't wait forever for trip, incase it doesn't
        # trip can be determined by current meas (?)

    def uv_trip_proc(self, env: Env, eut: Eut):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the EUT.
        '''

        '''
        k) Repeat steps c) through j) for each undervoltage operating trip region.
        '''
        '''
        c) Set (or verify) all EUT parameters to the nominal operating settings. If the undervoltage setting is
        adjustable, set the EUT to the maximum undervoltage setting but no greater than the nominal
        voltage minus twice the minimum required accuracy for voltage.
        '''
        for trip_region in trip_regions:
            '''
            d) Set the trip time setting to the minimum.
            '''
            '''
            j) Set the trip time setting to the maximum and repeat steps e) through i).
            '''
            for trip_time in trip_times:
                '''
                i) If the trip magnitude is adjustable, repeat steps e) through h) at minimum of the range.
                '''
                for trip_mag in trip_mags:
                    '''
                    h) For multiphase units, repeat steps d) through g) for the applicable voltage on each phase or phase
                    pair individually, and on all phases simultaneously.
                    '''
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    for _ in range(5):
                        '''
                        e) Record applicable settings.
                        For single-phase units, adjust the applicable voltage to parameter starting point Pb, as defined in
                        A.3, to a value less than or equal to the setpoint value determined in step c) plus 200% of the
                        MRA. The source shall be held at this voltage for a period th.
                        At the end of this period, initiate a step of the voltage to a level greater than or equal to the setpoint
                        value minus 200% of the MRA using the procedure specified in A.3. For multiphase units, adjust
                        voltage on one phase using the values above. Verify that remaining phases are held at nominal
                        ±0.02 p.u.
                        f) Record all voltage magnitudes when the unit trips.
                        '''
                        pass

    def ov_rthr_proc(self):
        """"""
        '''
        
        '''
        pass

    def uv_rthr_proc(self):
        """"""
        '''

        '''
        pass
