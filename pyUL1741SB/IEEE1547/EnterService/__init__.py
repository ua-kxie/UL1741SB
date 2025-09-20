"""
IEEE 1547.1-2020 5.6
"""

from pyUL1741SB import Eut, Env


"""
IEEE 1547.1-2020
Table 11 — Enter Service Test Cases
+-----+----------+-------+-------+--------+--------+--------+--------+--------+-------+-------+-------+------+
|Case |Desc      |ES_dly |ES_rmp |Rnd_dly |ES_V_hi |ES_V_lo |ES_F_hi |ES_F_lo |Init_V |Fin_V  |Init_F |Fin_F |
|     |          |(s)    |(s)    |(s)     |(p.u.)  |(p.u.)  |(Hz)    |(Hz)    |(p.u.) |(p.u.) |(Hz)   |(Hz)  |
+-----+----------+-------+-------+--------+--------+--------+--------+--------+-------+-------+-------+------+
|1    |(Default) |300    |300    |NA      |1.05    |0.917   |60.1    |59.5    |0.897  |0.937  |60.0   |60.0  |
|2    |          |0      |NA     |300     |1.05    |0.917   |60.1    |59.5    |1.0    |1.0    |59.48  |59.52 |
|3    |(Maxima)  |600    |1000   |NA      |1.06    |0.95    |61.0    |59.9    |1.08   |1.04   |60.0   |60.0  |
|4    |          |0      |NA     |1000    |1.06    |0.95    |61.0    |59.9    |1.0    |1.0    |61.02  |60.98 |
|5    |(Minima)  |0      |1      |NA      |1.05    |0.88    |60.1    |59.0    |0.86   |0.90   |60.0   |60.0  |
|6    |          |0      |NA     |1       |1.05    |0.88    |60.1    |59.0    |1.0    |1.0    |58.98  |59.92 |
+-----+----------+-------+-------+--------+--------+--------+--------+--------+-------+-------+-------+------+
NOTE - Voltages are in per unit (p.u.) of the nominal EUT ac voltage.
"""


class ESTest:
    class ESCriteriaSettings:
        def __init__(self, volts_h, volts_l, hertz_h, hertz_l):
            self.volts_h = volts_h
            self.volts_l = volts_l
            self.hertz_h = hertz_h
            self.hertz_l = hertz_l

    class ACSrcVals:
        def __init__(self, volts_init, volts_finl, hertz_init, hertz_finl):
            self.volts_init = volts_init
            self.volts_finl = volts_finl
            self.hertz_init = hertz_init
            self.hertz_finl = hertz_finl

    def __init__(self, delay, period, randelay, es_criteria_settings, ac_src_vals):
        self.es_delay = delay
        self.es_period = period
        self.es_randelay = randelay
        self.es_criteria_settings = es_criteria_settings
        self.ac_src_vals = ac_src_vals

    @staticmethod
    def TestCase1():
        """Test Case 1 (Defaults)"""
        return ESTest(
            delay=300,
            period=300,
            randelay=None,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.05,
                volts_l=0.917,
                hertz_h=60.1,
                hertz_l=59.5
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=0.897,
                volts_finl=0.937,
                hertz_init=60.0,
                hertz_finl=60.0
            )
        )

    @staticmethod
    def TestCase2():
        """Test Case 2"""
        return ESTest(
            delay=0,
            period=None,
            randelay=300,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.05,
                volts_l=0.917,
                hertz_h=60.1,
                hertz_l=59.5
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=1.0,
                volts_finl=1.0,
                hertz_init=59.48,
                hertz_finl=59.52
            )
        )

    @staticmethod
    def TestCase3():
        """Test Case 3 (Maxima)"""
        return ESTest(
            delay=600,
            period=1000,
            randelay=None,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.06,
                volts_l=0.95,
                hertz_h=61.0,
                hertz_l=59.9
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=1.08,
                volts_finl=1.04,
                hertz_init=60.0,
                hertz_finl=60.0
            )
        )

    @staticmethod
    def TestCase4():
        """Test Case 4"""
        return ESTest(
            delay=0,
            period=None,
            randelay=1000,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.06,
                volts_l=0.95,
                hertz_h=61.0,
                hertz_l=59.9
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=1.0,
                volts_finl=1.0,
                hertz_init=61.02,
                hertz_finl=60.98
            )
        )

    @staticmethod
    def TestCase5():
        """Test Case 5 (Minima)"""
        return ESTest(
            delay=0,
            period=1,
            randelay=None,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.05,
                volts_l=0.88,
                hertz_h=60.1,
                hertz_l=59.0
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=0.86,
                volts_finl=0.90,
                hertz_init=60.0,
                hertz_finl=60.0
            )
        )

    @staticmethod
    def TestCase6():
        """Test Case 6"""
        return ESTest(
            delay=0,
            period=None,
            randelay=1,
            es_criteria_settings=ESTest.ESCriteriaSettings(
                volts_h=1.05,
                volts_l=0.88,
                hertz_h=60.1,
                hertz_l=59.0
            ),
            ac_src_vals=ESTest.ACSrcVals(
                volts_init=1.0,
                volts_finl=1.0,
                hertz_init=58.98,
                hertz_finl=59.92
            )
        )

class ES:
    def es_proc(self, env: Env, eut: Eut):
        """"""
        for tc in [
            ESTest.TestCase1(),
            ESTest.TestCase2(),
            ESTest.TestCase3(),
            ESTest.TestCase4(),
            ESTest.TestCase5(),
            ESTest.TestCase6(),
        ]:
            '''
            a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
            b) Disable the permit service setting. Begin recording EUT active power, ac voltage, and frequency.
            '''
            eut.config_es(Ena=False)
            '''
            c) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
            EUT. Make available sufficient input power for the EUT to reach its rated active power.
            '''
            env.dc_config(pwr_watts=eut.Prated * 1.2)
            '''
            d) Apply the DER ES criteria settings, ES delay, and ES period or randomized delay specified in
            Table 11 for the test case under test.
            '''
            tc.es_delay
            tc.es_randelay
            tc.es_period
            tc.es_criteria_settings.volts_h
            tc.es_criteria_settings.volts_l
            tc.es_criteria_settings.hertz_h
            tc.es_criteria_settings.hertz_l
            '''
            e) Confirm that the EUT does not begin to export power by waiting for no less than the greater of:
                1) 60 s or
                2) 2 × (the ES delay time) plus the ES randomized delay setting (if enabled).
            '''
            max(60, 2 * tc.es_delay + (0 if tc.es_randelay is None else tc.es_randelay))
            '''
            f) Set the ac test source to the initial voltage and frequency specified in Table 11.
            '''
            env.ac_config(Vac=tc.ac_src_vals.volts_init, Freq=tc.ac_src_vals.hertz_init)
            '''
            g) Enable the permit service setting.
            '''
            eut.config_es(Ena=True)
            '''
            h) Confirm that the EUT does not begin to export power by waiting for no less than the greater of:
                1) 60 s or
                2) 2 × (the ES delay time) plus the ES randomized delay setting (if enabled).
            '''
            max(60, 2 * tc.es_delay + (0 if tc.es_randelay is None else tc.es_randelay))
            '''
            i) Set the ac test source to the final voltage and frequency specified in Table 11 for a duration equal
            to 25% of the ES delay. Return the ac test source to the initial voltage and frequency specified in
            Table 11 for a duration of 0.05 s to 0.1 s to allow the ES delay timer to restart. This step shall be
            omitted for test cases where the ES delay setting is zero.
            '''
            if tc.es_delay != 0:
                env.ac_config(Vac=tc.ac_src_vals.volts_finl, Freq=tc.ac_src_vals.hertz_finl)
                env.sleep(tc.es_delay * 0.25)
                env.ac_config(Vac=tc.ac_src_vals.volts_init, Freq=tc.ac_src_vals.hertz_init)
                env.sleep(tc.es_delay * 0.05)
            '''--- no export nor sync above here ---'''
            '''
            j) Set the ac test source to the final voltage and frequency specified in Table 11. Wait until EUT
            active power stabilizes at its rated value.
            '''
            env.ac_config(Vac=tc.ac_src_vals.volts_finl, Freq=tc.ac_src_vals.hertz_finl)
            # wait for prated, should take at least 0.985 * tc.es_delay
            '''
            k) Disable the permit service setting. Wait until the EUT ceases to energize the ac test source.
            '''
            eut.config_es(Ena=False)
            # wait for cessation
            '''
            l) Enable the permit service setting. Wait 5 s. This step shall be omitted for test cases where the ES
            delay setting is zero.
            '''
            if tc.es_delay != 0:
                eut.config_es(Ena=True)
                env.sleep(5)
            raise NotImplementedError

    def es_validate_step_j(self):
        """"""
        '''
        In step j), the EUT shall not begin to export active power until at least 98.5% of the ES delay has elapsed,
        starting from the point in time when the ac test source voltage and frequency returned to within the ES
        criteria range after the last excursion outside the ES criteria range. This also confirms that the EUT delay
        counter restarted following the excursion in step i) outside the ES criteria range.
        
        In step j), the measured EUT active power shall comply with all requirements in 4.10.3 c) in
        IEEE Std 1547-2018, including requirements on average rate-of-change of active power and maximum
        active power step increase. For test cases where the ES randomized delay is used, the active power shall
        comply with 4.10.3c Exception 1 in IEEE Std 1547-2018. For test cases where the ES period (ramp) is
        used, the EUT shall not reach its rated active power before a time has elapsed equal to 98.5% of the sum of
        the ES intentional delay time and the ES period, starting from the point in time when the ac test source
        voltage and frequency returned to within the to the ES criteria range for the test case.
        '''
        pass
'''
In steps b) through i) of 5.6.2, the EUT shall not export active power to the ac test source or initiate
synchronization.

In step j), the EUT shall not begin to export active power until at least 98.5% of the ES delay has elapsed,
starting from the point in time when the ac test source voltage and frequency returned to within the ES
criteria range after the last excursion outside the ES criteria range. This also confirms that the EUT delay
counter restarted following the excursion in step i) outside the ES criteria range.

In step j), the measured EUT active power shall comply with all requirements in 4.10.3 c) in
IEEE Std 1547-2018, including requirements on average rate-of-change of active power and maximum
active power step increase. For test cases where the ES randomized delay is used, the active power shall
comply with 4.10.3c Exception 1 in IEEE Std 1547-2018. For test cases where the ES period (ramp) is
used, the EUT shall not reach its rated active power before a time has elapsed equal to 98.5% of the sum of
the ES intentional delay time and the ES period, starting from the point in time when the ac test source
voltage and frequency returned to within the to the ES criteria range for the test case.

In step k), the EUT shall cease to energize the ac test source (i.e., active power shall fall to zero) within the
time specified in 4.6.1 of IEEE Std 1547-2018.

In step l), the EUT shall not export active power to the ac test source or initiate synchronization within the
specified 5 s wait time.
'''
