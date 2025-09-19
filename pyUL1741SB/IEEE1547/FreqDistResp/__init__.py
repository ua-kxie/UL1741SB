"""
IEEE 1547.1-2020 5.5
"""
from datetime import timedelta
from pyUL1741SB import Eut, Env

from pyUL1741SB.IEEE1547.base import IEEE1547Common

class FreqDist(IEEE1547Common):
    def oft_proc(self, env: Env, eut: Eut):
        '''
        '''
        shalltrip_tbl = eut.freqshalltrip_tbl
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source or signal injection generator parameters to the nominal operating conditions
        for the EUT.
        '''
        '''
        m) Repeat steps c) through l) for each overfrequency operating region.
        '''
        for trip_key, trip_region in {'OF2': shalltrip_tbl.OF2, 'OF1': shalltrip_tbl.OF1}.items():
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
            for trip_cts in list({trip_region.cts_min, trip_region.cts_max}):
                tMRA = eut.mra.static.T(trip_cts)
                '''
                k) Set (or verify) EUT parameters at the maximum of the overfrequency trip magnitude setting
                within the range of adjustment specified by the manufacturer and repeat steps e) through j).
                '''
                for trip_fpu in list({trip_region.hertz_min, trip_region.hertz_max}):
                    '''
                    j) Repeat steps d) through i) four times for a total of five tests.
                    '''
                    eut.set_ft(**{trip_key: {'freq': trip_fpu, 'cts': trip_cts}})
                    for i in range(5):
                        '''
                        d) Set (or verify) EUT parameters to the minimum [maximum] overfrequency trip magnitude setting within the
                        range of adjustment specified by the manufacturer.
                        e) Set (or verify) the EUT parameters to the minimum [maximum] overfrequency trip duration setting within the
                        range of adjustment specified by the manufacturer.
                        '''
                        dct_label = {'proc': 'oft', 'region': trip_key, 'time': trip_cts, 'mag': trip_fpu, 'iter': i}
                        env.pre_cbk(**dct_label)
                        self.oft_validate(env, eut, dct_label, trip_fpu, trip_cts, tMRA)
                        env.post_cbk(**dct_label)
                        self.trip_rst(env, eut)

    def oft_validate(self, env: Env, eut: Eut, dct_label, trip_fpu, trip_cts, tMRA):
        """"""
        # PN, PB, PU
        # th, cts
        '''
        f) Record applicable settings of the ac power source or signal injection generator and the EUT.
        g) Adjust the ac test source frequency from PN to PB. The ac test source shall be held at this
        frequency for period th.
        h) At the end of this period, increase the frequency to PU and hold for a period not less than 1.5 times
        the clearing time setting.
        i) Record the frequency at which the unit trips and the clearing time.
        
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within the
        respective clearing times for each underfrequency tripping range specified in IEEE Std 1547. The evaluated
        ranges of adjustment for tripping magnitude and duration shall be greater than or equal to the allowable
        ranges of adjustment for each underfrequency tripping range specified in IEEE Std 1547.
        
        A.4 (c) The hold time, th, shall be greater than or equal to 100% of the trip time setting plus 200%
        the minimum required measurement accuracy (MRA) for time, as specified in Table 3 of
        IEEE Std 1547-2018 for steady-state conditions.
        
        [...] PU is at least 110% (90% for under value tests) of PT. 
        Exception: For frequency tests, [...] PU is at least 101% (99% for under value tests) of PT.
        '''
        dur = timedelta(seconds=trip_cts + 2 * tMRA)
        env.ac_config(freq=eut.fN, rocof=eut.rocof())

        ts = env.time_now()
        env.ac_config(freq=trip_fpu * eut.fN * 0.99, rocof=eut.rocof())
        operating = not self.trip_validate(env, eut, dur, ts, tMRA)

        ts = env.time_now()
        env.ac_config(freq=trip_fpu * eut.fN * 1.1, rocof=eut.rocof())
        tripped = self.trip_validate(env, eut, dur, ts, tMRA)

        env.validate({**dct_label, 'operating': operating, 'tripped': tripped})

    def uft_proc(self, env: Env, eut: Eut):
        '''
        '''
        shalltrip_tbl = eut.freqshalltrip_tbl
        '''
        a) Connect the EUT according to the instructions and specifications provided by the
        manufacturer.
        b) Set all programmable ac power source or signal injection generator parameters to the nominal
        operating conditions for the EUT.
        '''
        '''
        m) Repeat steps c) through l) for each underfrequency operating region.
        '''
        for trip_key, trip_region in {'UF2': shalltrip_tbl.UF2, 'UF1': shalltrip_tbl.UF1}.items():
            '''
            c) Disable or program the relevant settings for all other active and reactive power control
            functions of the EUT to not influence the test results for the operating region being evaluated.
            Set the frequency droop function to the widest deadband setting and maximum droop setting
            to make the active power change with respect to frequency as small as possible.
            '''
            '''
            l) Set (or verify) the EUT parameters to the [minimum] maximum underfrequency trip duration setting
            within the range of adjustment specified by the manufacturer and repeat steps e) through k).
            '''
            for trip_cts in list({trip_region.cts_min, trip_region.cts_max}):
                tMRA = eut.mra.static.T(trip_cts)
                '''
                k) Set (or verify) EUT parameters at the [minimum] maximum of the underfrequency trip magnitude setting
                within the range of adjustment specified by the manufacturer and repeat steps e) through j).
                '''
                for trip_fpu in list({trip_region.hertz_min, trip_region.hertz_max}):
                    '''
                    j) Repeat steps d) through i) four times for a total of five tests.
                    '''
                    eut.set_ft(**{trip_key: {'freq': trip_fpu, 'cts': trip_cts}})
                    for i in range(5):
                        '''
                        d) Set (or verify) EUT parameters to the minimum underfrequency trip magnitude setting within
                        the range of adjustment specified by the manufacturer.
                        e) Set (or verify) EUT parameters to the minimum underfrequency trip duration setting within
                        the range of adjustment specified by the manufacturer.
                        f) Record applicable settings of the ac test source or signal injection generator and the EUT.
                        g) Adjust the source frequency from PN to PB. The source shall be held at this frequency for
                        period th.34
                        h) At the end of this period, decrease the frequency to PU and hold for a duration not less than
                        1.5 times the clearing time setting.
                        i) Record the frequency at which the unit trips and the clearing time.
                        '''
                        dct_label = {'proc': 'uft', 'region': trip_key, 'time': trip_cts, 'mag': trip_fpu, 'iter': i}
                        env.pre_cbk(**dct_label)
                        self.uft_validate(env, eut, dct_label, trip_fpu, trip_cts, tMRA)
                        env.post_cbk(**dct_label)

    def uft_validate(self, env: Env, eut: Eut, dct_label, trip_fpu, trip_cts, tMRA):
        """"""
        # PN, PB, PU
        # th, cts
        '''
        f) Record applicable settings of the ac test source or signal injection generator and the EUT.
        g) Adjust the source frequency from PN to PB. The source shall be held at this frequency for
        period th.34
        h) At the end of this period, decrease the frequency to PU and hold for a duration not less than
        1.5 times the clearing time setting.
        i) Record the frequency at which the unit trips and the clearing time.
        
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within the
        respective clearing times for each underfrequency tripping range specified in IEEE Std 1547. The evaluated
        ranges of adjustment for tripping magnitude and duration shall be greater than or equal to the allowable
        ranges of adjustment for each underfrequency tripping range specified in IEEE Std 1547.
        
        A.4 (c) The hold time, th, shall be greater than or equal to 100% of the trip time setting plus 200%
        the minimum required measurement accuracy (MRA) for time, as specified in Table 3 of
        IEEE Std 1547-2018 for steady-state conditions.
        
        [...] PU is at least 110% (90% for under value tests) of PT. 
        Exception: For frequency tests, [...] PU is at least 101% (99% for under value tests) of PT.
        '''
        dur = timedelta(seconds=trip_cts + 2 * tMRA)
        env.ac_config(freq=eut.fN, rocof=eut.rocof())

        ts = env.time_now()
        env.ac_config(freq=trip_fpu * eut.fN * 1.01, rocof=eut.rocof())
        operating = not self.trip_validate(env, eut, dur, ts, tMRA)

        ts = env.time_now()
        env.ac_config(freq=trip_fpu * eut.fN * 0.90, rocof=eut.rocof())
        tripped = self.trip_validate(env, eut, dur, ts, tMRA)
        env.validate({**dct_label, 'operating': operating, 'tripped': tripped})

    def hfrt_proc(self, env: Env, eut: Eut):
        """"""
        '''
        a) Connect the EUT to a load bank according to manufacturer’s instructions.
        b) Set or verify that the EUT is programmed using default settings.
        c) Set the frequency droop function and droop values to make the active power change with respect to
        frequency as small as possible.
        d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
        '''
        # TODO
        '''
        VFO CAPABLE:
        e) Operate the EUT at nominal frequency ± 0.6 Hz into a load bank load capable of absorbing 100%
        to 125% of the power rating of the EUT.

        VFO INCAPABLE:
        e) Operate the ac test source at nominal frequency ± 0.1 Hz.
        '''
        if eut.vfo:
            pass
        else:
            raise NotImplementedError

        '''
        i) Repeat steps f) and g) twice for a total of three tests.
        '''
        for _ in range(3):
            '''
            f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
            convenient power factor. Record the output current of the EUT at the nominal frequency condition.
            '''
            eut.active_power(pu=0.9)
            eut.fixed_pf(PF=1.0)
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
            if eut.vfo:
                pass
            else:
                raise NotImplementedError
        '''
        j) During all frequency transitions in steps f) through h), the ROCOF shall be greater than or equal to
        the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the demonstrated ROCOF
        capability of the EUT.
        '''
    def hfrt_validate(self):
        """"""
        '''
        j) During all frequency transitions in steps f) through h), the ROCOF shall be greater than or equal to
        the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the demonstrated ROCOF
        capability of the EUT.
        
        IEEE 1547-2020 5.5.4.6
        An EUT shall be considered in compliance when the EUT rides through the abnormal frequency excursions
        with a magnitude and duration not less than those specified in 6.5.2 of IEEE Std 1547-2018.
        
        When varying the frequency of the ac test source or EUT, the ROCOF should be kept below the ROCOF
        capability of the EUT to avoid nuisance tripping. The ROCOF used in the ride-through tests shall exceed
        the minimum ROCOF capability required in 6.5.2.5 of IEEE Std 1547-2018, to satisfy the ROCOF ridethrough
        test requirements for the EUT’s Abnormal Operating Performance Category.
        '''
        pass

    def lfrt_proc(self, env: Env, eut: Eut):
        """"""
        '''
        a) Connect the EUT to a load bank according to manufacturer’s instructions.
        b) Set or verify that the EUT is programmed using default settings.
        c) Set the frequency droop function and droop values to make the active power change with respect to
        frequency as small as possible.
        d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
        '''
        # TODO
        '''
        VFO CAPABLE:
        e) Operate the EUT at nominal frequency ± 0.6 Hz into a load bank load capable of absorbing 100%
        to 125% of the power rating of the EUT.

        VFO INCAPABLE:
        e) Operate the ac test source at nominal frequency ± 0.1 Hz.
        '''
        if eut.vfo:
            pass
        else:
            raise NotImplementedError
        '''
        i) Repeat steps f) and g) twice for a total of three tests. 
        '''
        for _ in range(3):
            '''
            f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
            convenient power factor. Record the output current of the EUT at the nominal frequency condition.
            '''
            eut.active_power(pu=0.9)
            eut.fixed_pf(PF=1.0)
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
            if eut.vfo:
                pass
            else:
                raise NotImplementedError
        '''
        j) During all frequency transitions in steps f) through h) the absolute ROCOF shall be 
        greater than or equal to the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the 
        demonstrated ROCOF capability of the EUT.
        '''

    def lfrt_validate(self):
        """"""
        '''
        j) During all frequency transitions in steps f) through h) the absolute ROCOF shall be 
        greater than or equal to the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the 
        demonstrated ROCOF capability of the EUT.

        IEEE 1547-2020 5.5.3.6
        An EUT shall be considered in compliance when the EUT rides through the abnormal frequency excursions
        with a magnitude and duration not less than those specified in 6.5.2 of IEEE Std 1547-2018.

        When varying the frequency of the ac test source or EUT, the ROCOF should be kept below the ROCOF
        capability of the EUT to avoid nuisance tripping. The ROCOF used in the ride-through tests shall exceed
        the minimum ROCOF capability required in 6.5.2.5 of IEEE Std 1547-2018, to satisfy the ROCOF ridethrough
        test requirements for the EUT’s Abnormal Operating Performance Category.
        '''
        pass

