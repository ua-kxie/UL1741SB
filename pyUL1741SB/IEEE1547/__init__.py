"""
IEEE 1547.1-2020 5.13
"""
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.VoltReg import VoltReg
from pyUL1741SB.IEEE1547.FreqDistResp import FreqDist
from pyUL1741SB.IEEE1547.VoltDistResp import VoltDist
from pyUL1741SB.IEEE1547.FreqSupp import FreqSupp
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.base import IEEE1547Common

from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve

from datetime import timedelta

import pandas as pd

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

class IEEE1547(VoltReg, FreqDist, VoltDist, FreqSupp, IEEE1547Common):
    def lap_proc(self, env: Env, eut: Eut):
        """"""
        dflt_fwchar = {
            eut.aopCat.I: FWChar.CatI_CharI(),
            eut.aopCat.II: FWChar.CatII_CharI(),
            eut.aopCat.III: FWChar.CatIII_CharI(),
        }[eut.aopCat]
        if eut.Prated_prime < 0:
            dflt_vwcrv = {
                eut.Category.A: VWCurve.Crv_1A_abs(eut),
                eut.Category.B: VWCurve.Crv_1B_abs(eut),
            }[eut.Cat]
        else:
            dflt_vwcrv = {
                eut.Category.A: VWCurve.Crv_1A_inj(eut),
                eut.Category.B: VWCurve.Crv_1B_inj(eut),
            }[eut.Cat]
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        Apply the default settings from IEEE Std 1547 for voltage-active power mode. Apply the default
        settings from frequency-droop response in IEEE Std 1547 for the abnormal operating performance
        category of the DER. Enable voltage-active power mode.
        '''
        env.ac_config(freq=eut.fN, Vac=eut.VN)
        '''
        g) Repeat steps b) through f) using active power limits of [66%] 33% and zero.
        h) Repeat steps b) through g) twice for a total of three repetitions.
        '''
        for i in range(3):
            for aplim_pu in [0.66, 0.33, 0]:
                '''
                b) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
                EUT. Make available sufficient input power for the EUT to reach its rated active power. Allow (or
                command) the EUT to reach steady-state output at its rated active power. Begin recording EUT
                active power.
                
                c) Apply an active power limit to the EUT of 66[, 33, 0]% of its rated active power. Wait until the EUT active
                power reaches a new steady state.
                
                d) Reduce the frequency of the ac test source to 59 Hz and hold until EUT active power reaches a new
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                
                e) Increase the frequency of the ac test source to 61 Hz and hold until EUT active power reaches
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                
                f) Increase the voltage of the ac test source to 1.08 times nominal and hold until EUT active power
                reaches steady state. Return ac test source voltage to nominal.
                '''
                # b)
                eut.set_ap(Ena=True, pu=1)  # TODO check appropriate setting for this step
                # TODO wait for SS state
                dct_label = {
                    'proc': 'lap',
                    'iter': i,
                    'aplim_pu': aplim_pu,
                }
                def y_of_fw(x):
                    if eut.Prated_prime < 0:
                        ymin_pu = -1
                    else:
                        ymin_pu = 0
                    ymax_pu = 1
                    fw_val = dflt_fwchar.y_of_x(x, ymin_pu, aplim_pu, ymax_pu) * eut.Prated
                    return fw_val
                def y_of_vw(x):
                    vw_val = dflt_vwcrv.y_of_x(x) * eut.Prated
                    return min(vw_val, aplim_pu * eut.Prated)
                lst_tup_steps = [
                    # step label, perturbation, y_ss_target, olrt
                    ('c', lambda: eut.set_lap(Ena=True, pu=aplim_pu), aplim_pu * eut.Prated, timedelta(seconds=30)),
                    ('d1', lambda: env.ac_config(freq=59, rocof=eut.rocof()), y_of_fw(59), timedelta(seconds=dflt_fwchar.tr)),
                    ('d2', lambda: env.ac_config(freq=60, rocof=eut.rocof()), y_of_fw(60), timedelta(seconds=dflt_fwchar.tr)),
                    ('e1', lambda: env.ac_config(freq=61, rocof=eut.rocof()), y_of_fw(61), timedelta(seconds=dflt_fwchar.tr)),
                    ('e2', lambda: env.ac_config(freq=60, rocof=eut.rocof()), y_of_fw(60), timedelta(seconds=dflt_fwchar.tr)),
                    ('f1', lambda: env.ac_config(Vac=1.08 * eut.VN), y_of_vw(1.08), timedelta(seconds=dflt_vwcrv.Tr)),
                    ('f2', lambda: env.ac_config(Vac=eut.VN), y_of_vw(1.0), timedelta(seconds=dflt_vwcrv.Tr))
                ]
                for tup in lst_tup_steps:
                    self.lap_validation(env, eut, dct_label, *tup)

    def lap_validation(self, env: Env, eut: Eut, dct_label, step_label, perturbation, y_ss_target, olrt: timedelta):
        """"""
        '''
        IEEE 1547.1-2018
        4.6.2 Capability to limit active power
        The DER shall be capable of limiting active power as a percentage of the nameplate active power rating.
        The DER shall limit its active power output to not greater than the active power limit set point in no more
        than 30 s or in the time it takes for the primary energy source to reduce its active power output to achieve
        the requirements of the active power limit set point, whichever is greater. In cases where the DER is
        supplying loads in the Local EPS, the active power limit set point may be implemented as a maximum
        active power export to the Area EPS. Under mutual agreement between the Area EPS operator and the
        DER operator, the DER may be required to reduce active power below the level needed to support Local
        EPS loads.
        '''
        '''
        In step c), the EUT steady-state active power shall be reduced to the commanded percentage of its rated
        power plus 1.5 × (MRA of active power) or less within a time that complies with 4.6.2 of IEEE Std 1547-
        2018.
        
        In steps d) and e), the EUT steady-state active power shall be modulated in accordance with the equations
        in Table 23 of IEEE Std 1547-2018 within the tolerance as defined in 4.2 of this standard. The response
        time shall comply with 4.6.2 of IEEE Std 1547-2018.
        
        In step f), the EUT steady-state active power shall be modulated in accordance with the applied volt-watt
        curve within the tolerance as defined in 4.2 of this standard. For the 66% power level, the expected power,
        Pexpected, is
        
        Pexpected = Prated – (Prated – P2)(Vmeas/Vnom – 1.06)/0.04
        
        where Prated is the EUT rated power, P2 is as defined in IEEE Std 1547-2018, Vmeas is the measured voltage
        at the RPA after the EUT power has reached steady state, and Vnom is the nominal voltage at the RPA. For
        the 33% and zero power levels, the EUT power is not expected to change.
        
        Where the EUT is DER equipment that does not produce power such as a plant controller, the EUT’s
        commanded active power may be used to verify operation. In such cases a design evaluation and/or
        commissioning test may be needed to verify correct operation of the installed DER.
        '''
        yarg = 'P'
        yMRA = eut.mra.static.P
        df_meas = self.meas_perturb(env, eut, perturbation, olrt, 4 * olrt, (yarg,))
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        ss_valid = y_ss <= y_ss_target + 1.5 * yMRA
        df_meas['y_target'] = y_ss_target
        env.validate(dct_label={
            **dct_label,
            'step': step_label,
            'y_init': y_init,
            'olrt': olrt.total_seconds(),
            'y_ss': y_ss,
            'y_ss_target': y_ss_target + 1.5 * yMRA,
            'ss_valid': ss_valid,
            'data': df_meas
        })

    def es_ramp_proc(self, env: Env, eut: Eut):
        """"""
        meas_args = ('P', 'F', 'V')
        for i, df_row in df_es_cases.iterrows():
            dct_label = {
                'proc': 'es-ramp',
                'case': df_row['case'],
            }
            '''
            a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
            b) Disable the permit service setting. Begin recording EUT active power, ac voltage, and frequency.
            c) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
            EUT. Make available sufficient input power for the EUT to reach its rated active power.
            '''
            eut.set_es(Ena=False)
            env.sleep(timedelta(seconds=5))
            ntrvl = timedelta(seconds=1)
            df_meas = self.meas_perturb(
                env, eut,
                lambda: env.ac_config(Vac=eut.VN, freq=eut.fN, rocof=eut.rocof()),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(eut, env, dct_label, step='c', df_meas=df_meas)
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
                env, eut,
                lambda: eut.set_es(**dct_es_settings),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(eut, env, dct_label, step='e', df_meas=df_meas)

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
                env.ac_config(Vac=vpu * eut.VN, freq=fhz, rocof=eut.rocof())
                eut.set_es(Ena=True)
            ntrvl = timedelta(seconds=max(60, 2 * df_row['ES delay (s)']))
            df_meas = self.meas_perturb(
                env, eut,
                perturb,
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(eut, env, dct_label, step='h', df_meas=df_meas)
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
                    env, eut,
                    lambda: env.ac_config(Vac=vpu * eut.VN, freq=fhz, rocof=eut.rocof()),
                    ntrvl, ntrvl, meas_args
                )

                vpu = df_row['Initial voltage (p.u.)']
                fhz = df_row['Initial frequency (Hz)']
                ntrvl = timedelta(seconds=0.05)
                df_meas1 = self.meas_perturb(
                    env, eut,
                    lambda: env.ac_config(Vac=vpu * eut.VN, freq=fhz, rocof=eut.rocof()),
                    ntrvl, ntrvl, meas_args
                )

                self.es_ramp_validate(eut, env, dct_label, step='i', df_meas=pd.concat([df_meas0, df_meas1]))
            '''
            j) Set the ac test source to the final voltage and frequency specified in Table 11. Wait until EUT
            active power stabilizes at its rated value.
            k) Disable the permit service setting. Wait until the EUT ceases to energize the ac test source.
            '''
            vpu = df_row['Final voltage (p.u.)']
            fhz = df_row['Final frequency (Hz)']
            ntrvl = timedelta(seconds=df_row['ES delay (s)'] + df_row['ES period (ramp) (s)'] + eut.olrt.lap)
            df_meas = self.meas_perturb(
                env, eut,
                lambda: env.ac_config(Vac=vpu * eut.VN, freq=fhz, rocof=eut.rocof()),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(eut, env, dct_label, step='j', df_meas=df_meas, ntrvl=timedelta(seconds=df_row['ES delay (s)'] + df_row['ES period (ramp) (s)']))
            # wait for ss at rated power
            ntrvl = timedelta(seconds=2 * 4)
            df_meas = self.meas_perturb(
                env, eut,
                lambda: eut.set_es(Ena=False),
                ntrvl, ntrvl, meas_args
            )
            self.es_ramp_validate(eut, env, dct_label, step='k', df_meas=df_meas, ntrvl=timedelta(seconds=2))
            # wait for cessation
            '''
            l) Enable the permit service setting. Wait 5 s. This step shall be omitted for test cases where the ES
            delay setting is zero.
            '''
            if df_row['ES delay (s)'] != 0:
                ntrvl = timedelta(seconds=5)
                df_meas = self.meas_perturb(
                    env, eut,
                    lambda: eut.set_es(Ena=True),
                    ntrvl, ntrvl, meas_args
                )
                self.es_ramp_validate(eut, env, dct_label, step='l', df_meas=df_meas)

    def es_ramp_validate(self, eut: Eut, env: Env, dct_label, step, df_meas, ntrvl=None):
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
            valid = (df_meas.loc[:, 'P'] < eut.mra.static.P).all()
        elif step in ['j']:
            idx985 = df_meas.index.asof(df_meas.index[1] + ntrvl * 0.985)
            limited = (df_meas.loc[:idx985, 'P'] < eut.Prated).all()
            valid = limited
        elif step in ['k']:
            valid = (df_meas.loc[df_meas.index.asof(df_meas.index[1] + ntrvl):, 'P'] < eut.mra.static.P).all()
        else:
            raise ValueError(f'Invalid step key {step}')

        df_meas.insert(0, 'case', dct_label['case'])
        env.validate(dct_label={
            **dct_label,
            'step': step,
            'valid': valid,
            'data': df_meas
        })

