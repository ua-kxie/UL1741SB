"""
IEEE 1547.1-2020 5.15
"""
from pyUL1741SB import Eut, Env
from datetime import timedelta
from typing import Callable
import numpy as np
import pandas as pd

from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB import viz


class FWChar:
    def __init__(self, dbof_hz, kof, dbuf_hz, kuf, tr):
        self.dbof_hz = dbof_hz
        self.kof = kof
        self.dbuf_hz = dbuf_hz
        self.kuf = kuf
        self.tr = tr

    def y_of_x(self, x, ymin, yn, ymax):
        """
        :param x: frequency in Hz
        :param ymin: eut minimum capable y, p.u.
        :param yn: y setpoint (p.u. at x within deadband)
        :param ymax: eut available y, p.u.
        :return: y (active power p.u.) at x (frequency, Hz)
        """
        def of_region():
            crv = yn - ((x - 60 - self.dbof_hz) / 60 / self.kof)
            return max(ymin, crv)
        def uf_region():
            crv = yn + ((60 - self.dbuf_hz - x) / 60 / self.kuf)
            return min(ymax, crv)
        df = x - 60
        if df < 0:  # UF
            df = abs(df)
            if df < self.dbuf_hz:
                return yn
            else:
                return uf_region()
        else:  # OF
            if df < self.dbof_hz:
                return yn
            else:
                return of_region()

    @staticmethod
    def CatI_CharI(): return FWChar(dbof_hz=0.036, kof=0.05, dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatII_CharI(): return FWChar(dbof_hz=0.036, kof=0.05, dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatIII_CharI(): return FWChar(dbof_hz=0.036, kof=0.05, dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatI_CharII(): return FWChar(dbof_hz=0.017, kof=0.03, dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatII_CharII(): return FWChar(dbof_hz=0.017, kof=0.03, dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatIII_CharII(): return FWChar(dbof_hz=0.017, kof=0.02, dbuf_hz=0.017, kuf=0.02, tr=0.2)

'''
The manufacturer shall state the following parameters of the EUT for this test:
Prated – Output power rating (W)
fN – Nominal frequency (Hz)
fH – Maximum frequency in the continuous operating region (Hz)
fL – Minimum frequency in the continuous operating region (Hz)
delta_Psmall – Small-signal performance (W)
delta_Plarge – Large-signal performance in % of rated power per minute
EUT’s abnormal operating performance category defined by IEEE Std 1547-2018
The additional parameter shall be calculated as follows:
delta_fsmall = delta_Psmall * fN * kOF
'''
class FreqSupp(IEEE1547):
    def fwo(self, outdir, final):
        self.validator = viz.Validator('fwo')
        try:
            self.fwo_proc()
        finally:
            final()
            self.validator.draw_new(outdir)

    def fwo_proc(self):
        """"""
        # chars = char1, char2, char1 with Pmin if needed
        fw_crvs = {
            self.c_eut.AOPCat.I: [FWChar.CatI_CharI(), FWChar.CatI_CharII(), FWChar.CatI_CharI()],
            self.c_eut.AOPCat.II: [FWChar.CatII_CharI(), FWChar.CatII_CharII(), FWChar.CatII_CharI()],
            self.c_eut.AOPCat.III: [FWChar.CatIII_CharI(), FWChar.CatIII_CharII(), FWChar.CatIII_CharI()],
        }[self.c_eut.aopCat]
        ap_sgns = [1, 1, -1]
        fw_crvs = list(zip(['charI', 'charII', 'charI'], fw_crvs, ap_sgns))
        if not self.c_eut.Prated_prime < 0:
            # discard second CharI run if eut cannot absorb active power
            fw_crvs = fw_crvs[:-1]
        # fw_crvs = [[crv_key, crv, p_min_pu]
        '''
        IEEE 1547.1-2020 5.15.3.2:
        "Frequency is ramped at the ROCOF for the category of the self.c_eut."
        '''
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all frequency trip parameters to the widest range of adjustability. Disable all reactive/active
        power control functions.
        '''
        self.conn_to_grid()
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
        '''
        r) For EUTs that can absorb power, rerun Characteristic 1 allowing the unit to absorb power by
        programming a negative Pmin.
        '''
        '''
        q) Repeat steps c) through p) for Characteristic 2.
        '''
        for crv_key, crv, ap_sgn in fw_crvs:
            pwrs_pu = ap_sgn * np.array([1.0, 0.2, 0.66])
            olrt = timedelta(seconds=crv.tr)
            '''
            p) Repeat test steps c) through o) with the EUT power set at 20% and 66% of rated power.
            '''
            for pwr_pu in pwrs_pu:
                '''
                c) Set all ac test source parameters to the nominal operating voltage and frequency.
                d) Adjust the EUT’s active power to Prated.
                e) Set EUT freq-watt parameters to the values specified by Characteristic 1. All other functions should
                be turned off.
                '''
                '''
                f) Verify freq-watt mode is reported as active and that the correct characteristic is reported.
                g) Once steady state is reached, read and record the EUT’s active power, reactive power, voltage,
                frequency, and current measurements.
                '''
                self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
                self.c_eut.set_ap(Ena=True, pu=pwr_pu)
                self.c_eut.set_fw(Ena=True, crv=crv)
                self.c_env.sleep(timedelta(seconds=self.c_eut.olrt.lap))  # wait for AP steady state
                y_of_x = lambda x: crv.y_of_x(x, -1, pwr_pu, 1) * self.c_eut.Prated
                dct_steps = self.fwo_traverse_steps(crv, af=self.c_eut.mra.static.F)
                for step_key, step_fcn in dct_steps.items():
                    dct_label = {'proc': 'fwo', 'crv': crv_key, 'pwr_pu': pwr_pu, 'step': step_key}
                    self.fwo_validate(dct_label, step_fcn, olrt, y_of_x)

    def fwo_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        5.15.2.3 Criteria
        Data from the test is used to confirm that the EUT follows the prescribed frequency-watt curve with the
        prescribed time responses. After each frequency step, a new steady-state active power, Pfinal, and a new
        expected steady-state active power, Pexpected(fsteady), shall be determined. fsteady may be determined from the
        ac test source frequency or the EUT’s reported frequency. The EUT’s reported frequency shall meet the
        accuracy requirements of IEEE Std 1547-2018 Table 3. To obtain a steady-state value, Pfinal may be
        measured at a time period much larger than the open loop response, Tr, setting of the frequency-watt
        function. As a guideline, for an EUT with a first-order linear response (which is not required), at 2 times
        the open loop response time setting, the steady-state state error is 1%. In addition, filtering may be used to
        reject any measurement variation during steady-state measurement.

        After the Δfsmall frequency ramps, the active power output at 1 times the open loop response (Tr), Psmall(Tr),
        shall be calculated as 90% × (Pfinal – Pinitial) + Pinitial. Psmall shall meet the test result accuracy requirements
        specified in 4.2 where Psmall is the Y parameter and Tr is the X parameter.
        
        For the larger frequency ramps, the EUT shall reach steady state within 1/ ΔPlarge minutes.
        '''
        self.fw_common_criteria(dct_label, perturb, olrt, y_of_x)

    def fwo_traverse_steps(self, crv: FWChar, af):
        """"""
        '''
        h) Begin the adjustment to fH. Ramp the frequency to af below (fN + dbOF).
        i) Ramp the frequency to af above (fN + dbOF).
        j) Ramp the frequency to Δfsmall + fN + dbOF.
        k) Ramp the frequency to fH.
        l) Begin the adjustment back to fN. Ramp the frequency to fH – Δfsmall.
        m) Ramp the frequency to af above (fN + dbOF).
        n) Ramp the frequency to af below (fN + dbOF).
        o) Ramp the frequency to fN.
        '''
        # delta_fsmall = delta_Psmall * fN * kOF
        delta_fsmall = self.c_eut.delta_Psmall * self.c_eut.fN * crv.kof
        ret = {
            'h': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN + crv.dbof_hz - af),
            'i': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN + crv.dbof_hz + af),
            'j': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN + crv.dbof_hz + delta_fsmall),
            'k': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fH),
            'l': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fH - delta_fsmall),
            'm': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN + crv.dbof_hz + af),
            'n': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN + crv.dbof_hz - af),
            'o': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN),
        }
        return ret

    def fwu(self, outdir, final):
        self.validator = viz.Validator('fwo')
        try:
            self.fwu_proc()
        finally:
            final()
            self.validator.draw_new(outdir)

    def fwu_proc(self):
        """"""
        fw_crvs = {
            self.c_eut.AOPCat.I: [FWChar.CatI_CharI(), FWChar.CatI_CharII(), FWChar.CatI_CharI()],
            self.c_eut.AOPCat.II: [FWChar.CatII_CharI(), FWChar.CatII_CharII(), FWChar.CatII_CharI()],
            self.c_eut.AOPCat.III: [FWChar.CatIII_CharI(), FWChar.CatIII_CharII(), FWChar.CatIII_CharI()],
        }[self.c_eut.aopCat]
        ap_sgns = [1, 1, -1]
        fw_crvs = list(zip(['charI', 'charII', 'charI'], fw_crvs, ap_sgns))
        if not self.c_eut.Prated_prime < 0:
            # discard second CharI run if eut can not absorb active power
            fw_crvs = fw_crvs[:-1]
        '''
        IEEE 1547.1-2020 5.15.3.2:
        "Frequency is ramped at the ROCOF for the category of the self.c_eut."
        '''
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all frequency trip parameters to the widest range of adjustability. Disable all reactive/active
        power control functions.
        '''
        self.conn_to_grid()
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
        '''
        o) Repeat steps b) through n) for Characteristic 2.
        p) For EUTs that can absorb power, rerun Characteristic 1 allowing the unit to absorb power by
        programming a negative Pmin. Set the unit to absorb power at −50% of Prated.
        '''
        # chars = char1, char2, char1 with Pmin if needed
        for crv_key, crv, ap_sgn in fw_crvs:
            pwr_pu = ap_sgn * 0.5
            olrt = timedelta(seconds=crv.tr)
            '''
            c) Set all ac test source parameters to the nominal operating voltage and frequency.
            d) Adjust the EUT’s available active power to Prated. Set the EUT’s output power to 50% of Prated.
            e) Set EUT frequency-watt parameters to the values specified by Characteristic 1. All other functions
            should be turned off.
            '''
            '''
            f) Verify frequency-watt mode is reported as active and that the correct characteristic is reported.
            '''
            self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
            self.c_eut.set_ap(Ena=True, pu=1.0)
            self.c_eut.set_lap(Ena=True, pu=pwr_pu)
            self.c_eut.set_fw(Ena=True, crv=crv)
            self.c_env.sleep(timedelta(seconds=self.c_eut.olrt.lap))  # wait for AP steady state
            y_of_x = lambda x: crv.y_of_x(x, -1, pwr_pu, 1) * self.c_eut.Prated
            dct_steps = self.fwu_traverse_steps(crv, af=self.c_eut.mra.static.F)
            for step_key, step_fcn in dct_steps.items():
                dct_label = {'proc': 'fwu', 'crv': crv_key, 'pwr_pu': pwr_pu, 'step': step_key}
                self.fwu_validate(dct_label, step_fcn, olrt, y_of_x)

    def fwu_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        5.15.3.3 Criteria
        Data from the test is used to confirm that the EUT follows the prescribed frequency-watt curve with the
        prescribed time responses. After each frequency step, a new steady-state active power, Pfinal, and a new
        expected steady-state active power, Pexpected(fsteady), shall be determined. fsteady may be determined from the
        ac test source frequency or the EUT’s reported frequency. To obtain a steady-state value, Pfinal may be
        measured at a time period much larger than the open loop response, Tr, setting of the frequency-watt
        function. As a guideline, at 2 times the open loop response time setting, the steady-state state error is 1%. In
        addition, filtering may be used to reject any measurement variation during steady-state measurement.
        
        After the Δfsmall frequency ramps, the active power output at 1 times the open loop response (Tr), Psmall(Tr),
        shall be calculated as 90% × (Pfinal – Pinitial) + Pinitial. Psmall shall meet the test result accuracy requirements
        specified in 4.2 where Psmall is the Y parameter and Tr is the X parameter.
        
        For the larger frequency ramps, the EUT shall reach steady state within 1/ ΔPlarge minutes.
        '''
        self.fw_common_criteria(dct_label, perturb, olrt, y_of_x)

    def fwu_traverse_steps(self, crv: FWChar, af):
        """"""
        '''
        g) Begin the adjustment to fL. Ramp the frequency to af above (fN – dbUF).
        h) Ramp the frequency to af below (fN – dbUF).
        i) Ramp the frequency to fN − Δfsmall – dbUF.
        j) Ramp the frequency to fL.
        k) Begin the adjustment back to fN. Ramp the frequency to fL + Δfsmall.
        l) Ramp the frequency to af below (fN – dbUF).
        m) Ramp the frequency to af above (fN – dbUF).
        n) Ramp the frequency to fN.
        '''
        # delta_fsmall = delta_Psmall * fN * kOF
        delta_fsmall = self.c_eut.delta_Psmall * self.c_eut.fN * crv.kof
        ret = {
            'g': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN - crv.dbof_hz + af),
            'h': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN - crv.dbof_hz - af),
            'i': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN - crv.dbof_hz - delta_fsmall),
            'j': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fL),
            'k': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fL + delta_fsmall),
            'l': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN - crv.dbof_hz - af),
            'm': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN - crv.dbof_hz + af),
            'n': lambda: self.c_env.ac_config(rocof=self.c_eut.rocof(), freq=self.c_eut.fN),
        }
        return ret

    def fw_common_criteria(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        xMRA = self.c_eut.mra.static.F
        yMRA = self.c_eut.mra.static.P
        tMRA = self.c_eut.mra.static.T(olrt.total_seconds())

        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'F', 'P'
        # need to apply different validation depending on DeltaPsmall/large
        # assume criteria for deltaPsmall for all steps, more stringent criteria
        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, ('P', 'Q', 'V', 'F'))

        t_init, t_olrt, t_ss0, t_ss1 = self.ts_of_interest(df_meas.index, olrt)
        # get y_init
        y_init = df_meas.loc[t_init, yarg]
        y_olrt = df_meas.loc[t_olrt, yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[t_ss0:, xarg].mean()
        y_ss = df_meas.loc[t_ss0:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 1.5*MRA at olrt within 1.5*MRA 
        '''
        olrt_s = olrt.total_seconds()
        y_of_t = lambda t: self.expapp(olrt_s, t, y_init, y_ss)
        y_olrt_min, y_olrt_max = self.range_4p2(y_of_t, olrt_s, tMRA, yMRA)
        y_olrt_target = y_of_t(olrt_s)
        olrt_valid = y_olrt <= y_olrt_max

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_ss_target = y_of_x(x_ss)
        y_ss_min, y_ss_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_ss <= y_ss_max

        self.validator.record_epoch(
            df_meas=df_meas,
            dct_crits={
                'P': pd.DataFrame({
                    'ts': [t_init, t_olrt, t_ss0, t_ss1],
                    'min': [y_init, y_olrt_min, y_ss_min, y_ss_min],
                    'targ': [y_init, y_olrt_target, y_ss_target, y_ss_target],
                    'max': [y_init, y_olrt_max, y_ss_max, y_ss_max],
                }).set_index('ts'),
            },
            start=t_init,
            end=t_ss1,
            label=''.join(f"{k}: {v}; " for k, v in {**dct_label, 'olrt_valid': olrt_valid, 'ss_valid': ss_valid}.items()),
            passed=olrt_valid and ss_valid
        )
