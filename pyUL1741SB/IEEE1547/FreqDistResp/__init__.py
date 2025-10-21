"""
IEEE 1547.1-2020 5.5
"""
from datetime import timedelta
from pyUL1741SB import Eut, Env

from pyUL1741SB.IEEE1547 import IEEE1547, TRIP_RPT

class FreqDist(IEEE1547):
    def oft_proc(self):
        '''
        '''
        shalltrip_tbl = self.c_eut.freqshalltrip_tbl
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source or signal injection generator parameters to the nominal operating conditions
        for the self.c_eut.
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
                tMRA = self.c_eut.mra.static.T(trip_cts)
                '''
                k) Set (or verify) EUT parameters at the maximum of the overfrequency trip magnitude setting
                within the range of adjustment specified by the manufacturer and repeat steps e) through j).
                '''
                for trip_fpu in list({trip_region.hertz_min, trip_region.hertz_max}):
                    '''
                    j) Repeat steps d) through i) four times for a total of five tests.
                    '''
                    self.c_eut.set_ft(**{trip_key: {'freq': trip_fpu, 'cts': trip_cts}})
                    for i in range(TRIP_RPT):
                        '''
                        d) Set (or verify) EUT parameters to the minimum [maximum] overfrequency trip magnitude setting within the
                        range of adjustment specified by the manufacturer.
                        e) Set (or verify) the EUT parameters to the minimum [maximum] overfrequency trip duration setting within the
                        range of adjustment specified by the manufacturer.
                        '''
                        dct_label = {'proc': 'oft', 'region': trip_key, 'time': trip_cts, 'mag': trip_fpu, 'iter': i}
                        self.oft_validate(dct_label, trip_fpu, trip_cts, tMRA)
                        self.trip_rst()

    def oft_validate(self, dct_label, trip_fpu, trip_cts, tMRA):
        """"""
        # PN, PB, PU
        # th, cts
        '''
        f) Record applicable settings of the ac power source or signal injection generator and the self.c_eut.
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
        self.c_env.ac_config(freq=self.c_eut.fN, rocof=self.c_eut.rocof())

        self.c_env.ac_config(freq=trip_fpu * self.c_eut.fN * 0.99, rocof=self.c_eut.rocof())
        self.c_env.sleep(dur)

        ts = self.c_env.time_now()
        self.c_env.ac_config(freq=trip_fpu * self.c_eut.fN * 1.1, rocof=self.c_eut.rocof())
        tripped = self.trip_validate(dur, ts, tMRA)
        ceased = self.cease_energize()

        self.c_env.validate({**dct_label, 'ceased': ceased, 'tripped': tripped})

    def uft_proc(self):
        '''
        '''
        shalltrip_tbl = self.c_eut.freqshalltrip_tbl
        '''
        a) Connect the EUT according to the instructions and specifications provided by the
        manufacturer.
        b) Set all programmable ac power source or signal injection generator parameters to the nominal
        operating conditions for the self.c_eut.
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
                tMRA = self.c_eut.mra.static.T(trip_cts)
                '''
                k) Set (or verify) EUT parameters at the [minimum] maximum of the underfrequency trip magnitude setting
                within the range of adjustment specified by the manufacturer and repeat steps e) through j).
                '''
                for trip_fpu in list({trip_region.hertz_min, trip_region.hertz_max}):
                    '''
                    j) Repeat steps d) through i) four times for a total of five tests.
                    '''
                    self.c_eut.set_ft(**{trip_key: {'freq': trip_fpu, 'cts': trip_cts}})
                    for i in range(TRIP_RPT):
                        '''
                        d) Set (or verify) EUT parameters to the minimum underfrequency trip magnitude setting within
                        the range of adjustment specified by the manufacturer.
                        e) Set (or verify) EUT parameters to the minimum underfrequency trip duration setting within
                        the range of adjustment specified by the manufacturer.
                        f) Record applicable settings of the ac test source or signal injection generator and the self.c_eut.
                        g) Adjust the source frequency from PN to PB. The source shall be held at this frequency for
                        period th.34
                        h) At the end of this period, decrease the frequency to PU and hold for a duration not less than
                        1.5 times the clearing time setting.
                        i) Record the frequency at which the unit trips and the clearing time.
                        '''
                        dct_label = {'proc': 'uft', 'region': trip_key, 'time': trip_cts, 'mag': trip_fpu, 'iter': i}
                        self.uft_validate(dct_label, trip_fpu, trip_cts, tMRA)

    def uft_validate(self, dct_label, trip_fpu, trip_cts, tMRA):
        """"""
        # PN, PB, PU
        # th, cts
        '''
        f) Record applicable settings of the ac test source or signal injection generator and the self.c_eut.
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
        self.c_env.ac_config(freq=self.c_eut.fN, rocof=self.c_eut.rocof())

        self.c_env.ac_config(freq=trip_fpu * self.c_eut.fN * 1.01, rocof=self.c_eut.rocof())
        self.c_env.sleep(dur)

        ts = self.c_env.time_now()
        self.c_env.ac_config(freq=trip_fpu * self.c_eut.fN * 0.90, rocof=self.c_eut.rocof())
        tripped = self.trip_validate(dur, ts, tMRA)
        ceased = self.cease_energize()

        self.c_env.validate({**dct_label, 'ceased': ceased, 'tripped': tripped})

    def hfrt_proc(self):
        """"""
        ft_tbl = self.c_eut.freqshalltrip_tbl
        ft_args = {
            'OF1': {'cts': ft_tbl.OF1.cts_max, 'freq': ft_tbl.OF1.hertz_min},
            'OF2': {'cts': ft_tbl.OF2.cts_max, 'freq': ft_tbl.OF2.hertz_min}
        }
        '''
        VFO CAPABLE:
        a) Connect the EUT to a load bank according to manufacturer’s instructions.
        VFO INCAPABLE:
        a) Connect the EUT to ac test source according to manufacturer’s instructions.
        '''
        '''
        b) Set or verify that the EUT is programmed using default settings.
        c) Set the frequency droop function and droop values to make the active power change with respect to
        frequency as small as possible.
        d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
        '''
        # TODO verify default settings
        self.c_eut.set_fw(Ena=False)
        self.c_eut.set_ft(**ft_args)
        '''
        VFO CAPABLE:
        e) Operate the EUT at nominal frequency ± 0.6 Hz into a load bank load capable of absorbing 100%
        to 125% of the power rating of the self.c_eut.

        VFO INCAPABLE:
        e) Operate the ac test source at nominal frequency ± 0.1 Hz.
        '''
        if self.c_eut.vfo_capable:
            raise NotImplementedError
        else:
            self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())

        '''
        i) Repeat steps f) and g) twice for a total of three tests.
        '''
        for iteration in range(3):
            '''
            f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
            convenient power factor. Record the output current of the EUT at the nominal frequency condition.
            '''
            self.c_eut.set_ap(Ena=True, pu=1.0)
            self.c_eut.set_cpf(Ena=True, PF=1.0)
            '''
            VFO CAPABLE:
            g) Adjust the EUT frequency from PN to PU where PU is greater than or equal to 61.8 Hz. The EUT
            shall be held at this frequency or period th, which shall be not less than 299 s.
            NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
            capability of the self.c_eut.
            h) Decrease the frequency of the EUT to the nominal frequency ± 0.6 Hz.
    
            VFO INCAPABLE:
            g) Adjust the source frequency from PN to PU where fU is greater than or equal to 61.8 Hz. The source
            shall be held at this frequency for period th, which shall be not less than 299 s.
            NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
            capability of the self.c_eut.
            h) Decrease the frequency of the ac test source to the nominal frequency ± 0.1 Hz.
            '''
            if self.c_eut.vfo_capable:
                raise NotImplementedError
            else:
                self.hfrt_validate(
                    {'proc': 'hfrt', 'iter': iteration, 'step': 'g'},
                    lambda: self.c_env.ac_config(freq=62, rocof=self.c_eut.rocof()),
                    timedelta(seconds=299)
                )
                self.hfrt_validate(
                    {'proc': 'hfrt', 'iter': iteration, 'step': 'h'},
                    lambda: self.c_env.ac_config(freq=self.c_eut.fN, rocof=self.c_eut.rocof()),
                    timedelta(seconds=1)
                )
        '''
        j) During all frequency transitions in steps f) through h), the ROCOF shall be greater than or equal to
        the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the demonstrated ROCOF
        capability of the self.c_eut.
        '''

    def hfrt_validate(self, dct_label, perturbation, ntrvl):
        """"""
        '''
        j) During all frequency transitions in steps f) through h), the ROCOF shall be greater than or equal to
        the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the demonstrated ROCOF
        capability of the self.c_eut.

        IEEE 1547-2020 5.5.4.6
        An EUT shall be considered in compliance when the EUT rides through the abnormal frequency excursions
        with a magnitude and duration not less than those specified in 6.5.2 of IEEE Std 1547-2018.

        When varying the frequency of the ac test source or EUT, the ROCOF should be kept below the ROCOF
        capability of the EUT to avoid nuisance tripping. The ROCOF used in the ride-through tests shall exceed
        the minimum ROCOF capability required in 6.5.2.5 of IEEE Std 1547-2018, to satisfy the ROCOF ridethrough
        test requirements for the EUT’s Abnormal Operating Performance Category.
        '''
        self.frt_validate(dct_label, perturbation, ntrvl)

    def lfrt_proc(self):
        """"""
        ft_tbl = self.c_eut.freqshalltrip_tbl
        ft_args = {
            'UF1': {'cts': ft_tbl.UF1.cts_max, 'freq': ft_tbl.UF1.hertz_min},
            'UF2': {'cts': ft_tbl.UF2.cts_max, 'freq': ft_tbl.UF2.hertz_min}
        }
        '''
        VFO CAPABLE:
        a) Connect the EUT to a load bank according to manufacturer’s instructions.
        VFO INCAPABLE:
        a) Connect the EUT to ac test source according to manufacturer’s instructions.
        '''
        '''
        b) Set or verify that the EUT is programmed using default settings.
        c) Set the frequency droop function and droop values to make the active power change with respect to
        frequency as small as possible.
        d) Set or verify that all frequency trip settings are set to not influence the outcome of the test.
        '''
        # TODO verify default settings
        self.c_eut.set_fw(Ena=False)
        self.c_eut.set_ft(**ft_args)
        '''
        VFO CAPABLE:
        e) Operate the EUT at nominal frequency ± 0.6 Hz into a load bank load capable of absorbing 100%
        to 125% of the power rating of the self.c_eut.

        VFO INCAPABLE:
        e) Operate the ac test source at nominal frequency ± 0.1 Hz.
        '''
        if self.c_eut.vfo_capable:
            raise NotImplementedError
        else:
            self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        '''
        i) Repeat steps f) and g) twice for a total of three tests. 
        '''
        for iteration in range(3):
            '''
            f) Operate EUT at any convenient power level between 90% and 100% of EUT rating and at any
            convenient power factor. Record the output current of the EUT at the nominal frequency condition.
            '''
            self.c_eut.set_ap(Ena=True, pu=1.0)
            self.c_eut.set_cpf(Ena=True, PF=1.0)
            '''
            VFO CAPABLE:
            g) Adjust the frequency of the EUT from PN to PU where PU is less than or equal to 57 Hz. The EUT
            shall be held at this frequency for period th, which shall be not less than 299 s.
            NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
            capability of the self.c_eut.
            h) Increase the frequency of the EUT to the nominal frequency ± 0.6 Hz.
    
            VFO INCAPABLE:
            g) Adjust the frequency of the ac test source from PN to PU where PU is less than or equal to 57 Hz.
            The source shall be held at this frequency for period th, which shall be not less than 299 s.
            NOTE—The ROCOF used during steps f) and g) may be used to demonstrate the ROCOF ride though
            capability of the self.c_eut.
            h) Increase the frequency of the ac test source to the nominal frequency ± 0.1 Hz.
            '''
            if self.c_eut.vfo_capable:
                raise NotImplementedError
            else:
                self.lfrt_validate(
                    {'proc': 'lfrt', 'iter': iteration, 'step': 'g'},
                    lambda: self.c_env.ac_config(freq=56.8, rocof=self.c_eut.rocof()),
                    timedelta(seconds=299)
                )
                self.lfrt_validate(
                    {'proc': 'lfrt', 'iter': iteration, 'step': 'h'},
                    lambda: self.c_env.ac_config(freq=self.c_eut.fN, rocof=self.c_eut.rocof()),
                    timedelta(seconds=1)
                )
        '''
        j) During all frequency transitions in steps f) through h) the absolute ROCOF shall be 
        greater than or equal to the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the 
        demonstrated ROCOF capability of the self.c_eut.
        '''

    def lfrt_validate(self, dct_label, perturbation, ntrvl):
        """"""
        '''
        j) During all frequency transitions in steps f) through h) the absolute ROCOF shall be 
        greater than or equal to the ROCOF limit in Table 21 of IEEE Std 1547-2018 and shall be within the 
        demonstrated ROCOF capability of the self.c_eut.

        IEEE 1547-2020 5.5.3.6
        An EUT shall be considered in compliance when the EUT rides through the abnormal frequency excursions
        with a magnitude and duration not less than those specified in 6.5.2 of IEEE Std 1547-2018.

        When varying the frequency of the ac test source or EUT, the ROCOF should be kept below the ROCOF
        capability of the EUT to avoid nuisance tripping. The ROCOF used in the ride-through tests shall exceed
        the minimum ROCOF capability required in 6.5.2.5 of IEEE Std 1547-2018, to satisfy the ROCOF ridethrough
        test requirements for the EUT’s Abnormal Operating Performance Category.
        '''
        self.frt_validate(dct_label, perturbation, ntrvl)

    def frt_validate(self, dct_label, perturbation, ntrvl):
        """"""
        df_meas = self.meas_perturb(perturbation, ntrvl, ntrvl, ('P', 'Q', 'F'))
        valid = ((df_meas.loc[:, 'P'] - self.c_eut.Prated) < 1.5 * self.c_eut.mra.static.P).all()

        self.c_env.validate(dct_label={
            **dct_label,
            'valid': valid,
            'data': df_meas,
        })
