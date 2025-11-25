"""
IEEE 1547.1-2020 5.6
"""
from datetime import timedelta

from pyUL1741SB import Eut, Env
import pandas as pd

from pyUL1741SB.IEEE1547 import IEEE1547

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

df_es_cases = pd.DataFrame({
    'case': [1, 2, 3, 4, 5, 6],
    'ES delay (s)': [300, 0, 600, 0, 0, 0],
    'ES period (ramp) (s)': [300, 300, 1000, 1000, 1, 1],  # same values for randomized delay
    'ES voltage high (p.u.)': [1.05, 1.05, 1.06, 1.06, 1.05, 1.05],
    'ES voltage low (p.u.)': [0.917, 0.917, 0.95, 0.95, 0.88, 0.88],
    'ES frequency high (Hz)': [60.1, 60.1, 61.0, 61.0, 60.1, 60.1],
    'ES frequency low (Hz)': [59.5, 59.5, 59.9, 59.9, 59.0, 59.0],
    'Initial voltage (p.u.)': [0.897, 1.0, 1.08, 1.0, 0.86, 1.0],
    'Final voltage (p.u.)': [0.937, 1.0, 1.04, 1.0, 0.90, 1.0],
    'Initial frequency (Hz)': [60.0, 59.48, 60.0, 61.02, 60.0, 58.98],
    'Final frequency (Hz)': [60.0, 59.52, 60.0, 60.98, 60.0, 59.92]
})

class ES(IEEE1547):
    def es_ramp_proc(self):
        """"""
        meas_args = ('P', 'Q', 'F', 'V')
        for i, df_row in df_es_cases.iterrows():
            dct_label = {
                'proc': 'es-ramp',
                'case': df_row['case'],
            }
            '''
            a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
            b) Disable the permit service setting. Begin recording EUT active power, ac voltage, and frequency.
            c) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
            self.c_eut. Make available sufficient input power for the EUT to reach its rated active power.
            '''
            self.conn_to_grid()
            self.c_eut.set_es(Ena=False)
            self.c_env.sleep(timedelta(seconds=5))
            ntrvl = timedelta(seconds=1)
            df_meas = self.meas_perturb(
                lambda: self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof()),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(dct_label, step='c', df_meas=df_meas)
            '''
            d) Apply the DER ES criteria settings, ES delay, and ES period or randomized delay specified in
            Table 11 for the test case under test.
            e) Confirm that the EUT does not begin to export power by waiting for no less than the greater of:
                1) 60 s or
                2) 2 × (the ES delay time) plus the ES randomized delay setting (if enabled).
            '''
            settings_keys = {
                'ES delay (s)': 'esDelay',
                'ES period (ramp) (s)': 'esPeriod',
                'ES voltage high (p.u.)': 'esVpuHi',
                'ES voltage low (p.u.)': 'esVpuLo',
                'ES frequency high (Hz)': 'esfHzHi',
                'ES frequency low (Hz)': 'esfHzLo',
            }
            dct_es_settings = {v: df_row[k] for k, v in settings_keys.items()}
            ntrvl = timedelta(seconds=max(60, 2 * df_row['ES delay (s)']))
            df_meas = self.meas_perturb(
                lambda: self.c_eut.set_es(**dct_es_settings),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(dct_label, step='e', df_meas=df_meas)

            '''
            f) Set the ac test source to the initial voltage and frequency specified in Table 11.
            g) Enable the permit service setting.
            h) Confirm that the EUT does not begin to export power by waiting for no less than the greater of:
                1) 60 s or
                2) 2 × (the ES delay time) plus the ES randomized delay setting (if enabled).
            '''
            vpu = df_row['Initial voltage (p.u.)']
            fhz = df_row['Initial frequency (Hz)']

            def perturb():
                self.c_env.ac_config(Vac=vpu * self.c_eut.VN, freq=fhz, rocof=self.c_eut.rocof())
                self.c_eut.set_es(Ena=True)

            ntrvl = timedelta(seconds=max(60, 2 * df_row['ES delay (s)']))
            df_meas = self.meas_perturb(
                perturb,
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(dct_label, step='h', df_meas=df_meas)
            '''
            i) Set the ac test source to the final voltage and frequency specified in Table 11 for a duration equal
            to 25% of the ES delay. Return the ac test source to the initial voltage and frequency specified in
            Table 11 for a duration of 0.05 s to 0.1 s to allow the ES delay timer to restart. This step shall be
            omitted for test cases where the ES delay setting is zero.
            '''
            if df_row['ES delay (s)'] != 0:
                vpu = df_row['Final voltage (p.u.)']
                fhz = df_row['Final frequency (Hz)']
                ntrvl = timedelta(seconds=df_row['ES delay (s)'] * 0.25)
                df_meas0 = self.meas_perturb(
                    lambda: self.c_env.ac_config(Vac=vpu * self.c_eut.VN, freq=fhz, rocof=self.c_eut.rocof()),
                    ntrvl, ntrvl, meas_args
                )

                vpu = df_row['Initial voltage (p.u.)']
                fhz = df_row['Initial frequency (Hz)']
                ntrvl = timedelta(seconds=0.05)
                df_meas1 = self.meas_perturb(
                    lambda: self.c_env.ac_config(Vac=vpu * self.c_eut.VN, freq=fhz, rocof=self.c_eut.rocof()),
                    ntrvl, ntrvl, meas_args
                )

                self.es_ramp_validate(dct_label, step='i', df_meas=pd.concat([df_meas0, df_meas1]))
            '''
            j) Set the ac test source to the final voltage and frequency specified in Table 11. Wait until EUT
            active power stabilizes at its rated value.
            k) Disable the permit service setting. Wait until the EUT ceases to energize the ac test source.
            '''
            vpu = df_row['Final voltage (p.u.)']
            fhz = df_row['Final frequency (Hz)']
            ntrvl = timedelta(seconds=df_row['ES delay (s)'] + df_row['ES period (ramp) (s)'] + self.c_eut.olrt.lap)
            df_meas = self.meas_perturb(
                lambda: self.c_env.ac_config(Vac=vpu * self.c_eut.VN, freq=fhz, rocof=self.c_eut.rocof()),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(dct_label, step='j', df_meas=df_meas,
                                  ntrvl=timedelta(seconds=df_row['ES delay (s)'] + df_row['ES period (ramp) (s)']))
            # wait for ss at rated power
            ntrvl = timedelta(seconds=2 * 4)
            df_meas = self.meas_perturb(
                lambda: self.c_eut.set_es(Ena=False),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(dct_label, step='k', df_meas=df_meas, ntrvl=timedelta(seconds=2))
            # wait for cessation
            '''
            l) Enable the permit service setting. Wait 5 s. This step shall be omitted for test cases where the ES
            delay setting is zero.
            '''
            if df_row['ES delay (s)'] != 0:
                ntrvl = timedelta(seconds=5)
                df_meas = self.meas_perturb(
                    lambda: self.c_eut.set_es(Ena=True),
                    ntrvl, ntrvl, meas_args
                )
                self.es_ramp_validate(dct_label, step='l', df_meas=df_meas)

    def es_ramp_validate(self, dct_label, step, df_meas, ntrvl=None):
        """"""
        '''
        In steps b) through i) of 5.6.2, the EUT shall not export active power to the ac test source or initiate
        synchronization.

        In step j), the EUT shall not begin to export active power until at least 98.5% of the ES delay has elapsed,
        starting from the point in time when the ac test source voltage and frequency returned to within the ES
        criteria range after the last excursion outside the ES criteria range. This also confirms that the EUT delay
        counter restarted following the excursion in step i) outside the ES criteria range.

        In step j), the measured EUT active power shall comply with all requirements in 4.10.3 c) in
        IEEE Std 1547-2018, including requirements on average rate-of-change of active power and maximum
        active power step increase. 

        For test cases where the ES randomized delay is used, the active power shall comply with 4.10.3c Exception 1 in 
        IEEE Std 1547-2018. 

        For test cases where the ES period (ramp) is used, the EUT shall not reach its rated active power before a time 
        has elapsed equal to 98.5% of the sum of the ES intentional delay time and the ES period, starting from the 
        point in time when the ac test source voltage and frequency returned to within the to the ES criteria range for 
        the test case.

        In step k), the EUT shall cease to energize the ac test source (i.e., active power shall fall to zero) within the
        time specified in 4.6.1 of IEEE Std 1547-2018.

        In step l), the EUT shall not export active power to the ac test source or initiate synchronization within the
        specified 5 s wait time.
        '''
        '''
        4.6.1 Capability to disable permit service
        The DER shall be capable of disabling the permit service setting and shall cease to energize the Area EPS
        and trip in no more than 2 s.
        '''
        if step in ['c', 'e', 'h', 'i', 'l']:
            # no energization expected
            valid = (df_meas.loc[:, 'P'] < self.c_eut.mra.static.P).all()
        elif step in ['j']:
            idx985 = df_meas.index.asof(df_meas.index[1] + ntrvl * 0.985)
            limited = (df_meas.loc[:idx985, 'P'] < self.c_eut.Prated).all()
            valid = limited
        elif step in ['k']:
            valid = (df_meas.loc[df_meas.index.asof(df_meas.index[1] + ntrvl):, 'P'] < self.c_eut.mra.static.P).all()
        else:
            raise ValueError(f'Invalid step key {step}')

        df_meas.insert(0, 'case', dct_label['case'])
        self.c_env.validate(dct_label={
            **dct_label,
            'step': step,
            'valid': valid,
            'data': df_meas
        })
