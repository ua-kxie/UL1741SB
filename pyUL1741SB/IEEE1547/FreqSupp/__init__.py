"""
IEEE 1547.1-2020 5.15
"""
from pyUL1741SB import Eut, Env
from datetime import timedelta
from typing import Callable
from pyUL1741SB.IEEE1547.base import IEEE1547Common

class FWChar:
    def __init__(self, dbof_hz, kof, dbuf_hz, kuf, tr):
        self.dbof_hz = dbof_hz
        self.kof = kof
        self.dbuf_hz = dbuf_hz
        self.kuf = kuf
        self.tr = tr

    def y_of_x(self, x, xn, ymin, yn):
        """
        :param x: frequency in Hz
        :param xn:
        :param ymin: eut minimum capable y, p.u.
        :param yn: y setpoint (p.u. at x within deadband)
        :return: y (active power p.u.) at x (frequency, Hz)
        """
        df = x - xn
        if df < 0:  # UF
            df = abs(df)
            if df < self.dbuf_hz:
                return yn
            else:
                return min(yn + (df - self.dbuf_hz) * self.kuf, 1.0)
        else:  # OF
            if df < self.dbof_hz:
                return yn
            else:
                return max(yn + (df - self.dbof_hz) * self.kof, ymin)

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
class FW(IEEE1547Common):
    def fwo_proc(self, env: Env, eut: Eut):
        """"""
        # chars = char1, char2, char1 with Pmin if needed
        fw_crvs = {
            Eut.AOPCat.I: [FWChar.CatI_CharI(), FWChar.CatI_CharII(), FWChar.CatI_CharI()],
            Eut.AOPCat.II: [FWChar.CatII_CharI(), FWChar.CatII_CharII(), FWChar.CatII_CharI()],
            Eut.AOPCat.III: [FWChar.CatIII_CharI(), FWChar.CatIII_CharII(), FWChar.CatIII_CharI()],
        }[eut.aopCat]
        p_mins_pu = [eut.Pmin/eut.Prated, eut.Pmin/eut.Prated, eut.Pmin_prime/eut.Prated]
        fw_crvs = list(zip(['charI', 'charII', 'charI'], fw_crvs, p_mins_pu))
        if not eut.Pmin_prime < 0:
            # discard second CharI run if eut cannot absorb active power
            fw_crvs = fw_crvs[:-1]
        # fw_crvs = [[crv_key, crv, p_min_pu]
        '''
        IEEE 1547.1-2020 5.15.3.2:
        "Frequency is ramped at the ROCOF for the category of the EUT."
        '''
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all frequency trip parameters to the widest range of adjustability. Disable all reactive/active
        power control functions.
        '''
        '''
        r) For EUTs that can absorb power, rerun Characteristic 1 allowing the unit to absorb power by
        programming a negative Pmin.
        '''
        '''
        q) Repeat steps c) through p) for Characteristic 2.
        '''
        pwrs_pu = [1.0, 0.2, 0.66]
        for crv_key, crv, p_min_pu in fw_crvs:
            eut.set_fw(Ena=True, crv=crv)
            olrt = timedelta(seconds=crv.tr)
            # TODO program eut's pmin

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
                y_of_x = lambda x: crv.y_of_x(x, eut.fN, p_min_pu, pwr_pu)
                dct_steps = self.fwo_traverse_steps(env, eut, crv, af=eut.mra.static.F)
                for step_key, step_fcn in dct_steps.items():
                    dct_label = {'proc': 'fwo', 'crv': crv_key, 'pmin': p_min_pu, 'pwr_pu': pwr_pu, 'step': step_key}
                    self.fwo_validate(env, eut, dct_label, step_fcn, olrt, y_of_x)

    def fwo_validate(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
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
        xMRA = eut.mra.static.F
        yMRA = eut.mra.static.P
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'F', 'P'
        # need to apply different validation depending on DeltaPsmall/large
        # assume criteria for deltaPsmall for all steps, more stringent criteria
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, (xarg, yarg))

        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[1] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[1] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 1.5*MRA at olrt within 1.5*MRA 
        '''
        y_olrt_targ = y_init + 0.9 * (y_ss - y_init)
        y_min, y_max = y_olrt_targ - 1.5 * yMRA, y_olrt_targ + 1.5 * yMRA
        olrt_valid = y_min <= y_olrt <= y_max

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_targ = y_of_x(x_ss)
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_min <= y_ss <= y_max
        env.validate(dct_label={
            **dct_label,
            'y_init': y_init,
            'y_olrt': y_olrt,
            'y_olrt_target': y_olrt_targ,
            'olrt_valid': olrt_valid,
            'y_ss': y_ss,
            'y_ss_target': y_targ,
            'ss_valid': ss_valid,
            'data': df_meas
        })

    def fwo_traverse_steps(self, env: Env, eut: Eut, crv: FWChar, af):
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
        delta_fsmall = eut.delta_Psmall * eut.fN * crv.kof
        ret = {
            'h': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN + crv.dbof_hz - af),
            'i': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN + crv.dbof_hz + af),
            'j': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN + crv.dbof_hz + delta_fsmall),
            'k': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fH),
            'l': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fH - delta_fsmall),
            'm': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN + crv.dbof_hz + af),
            'n': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN + crv.dbof_hz - af),
            'o': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN),
        }
        return ret

    def fwu_proc(self, env: Env, eut: Eut):
        """"""
        '''
        IEEE 1547.1-2020 5.15.3.2:
        "Frequency is ramped at the ROCOF for the category of the EUT."
        '''
        fw_crvs = {
            Eut.AOPCat.I: [FW_UF.CatI_CharI(), FW_UF.CatI_CharII(), FW_UF.CatI_CharI()],
            Eut.AOPCat.II: [FW_UF.CatII_CharI(), FW_UF.CatII_CharII(), FW_UF.CatII_CharI()],
            Eut.AOPCat.III: [FW_UF.CatIII_CharI(), FW_UF.CatIII_CharII(), FW_UF.CatIII_CharI()],
        }[eut.aopCat]
        p_mins_pu = [eut.Pmin / eut.Prated, eut.Pmin / eut.Prated, -0.5]
        fw_crvs = list(zip(fw_crvs, p_mins_pu))
        if not eut.Pmin_prime < 0:
            # discard second CharI run if eut can not absorb active power
            fw_crvs = fw_crvs[:-1]
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all frequency trip parameters to the widest range of adjustability. Disable all reactive/active
        power control functions.
        '''
        '''
        o) Repeat steps b) through n) for Characteristic 2.
        p) For EUTs that can absorb power, rerun Characteristic 1 allowing the unit to absorb power by
        programming a negative Pmin. Set the unit to absorb power at −50% of Prated.
        '''
        # chars = char1, char2, char1 with Pmin if needed
        for p_min_pu, crv in fw_crvs:
            '''
            c) Set all ac test source parameters to the nominal operating voltage and frequency.
            d) Adjust the EUT’s available active power to Prated. Set the EUT’s output power to 50% of Prated.
            e) Set EUT frequency-watt parameters to the values specified by Characteristic 1. All other functions
            should be turned off.
            '''
            env.dc_config(pwr_watts=eut.Prated)
            eut.active_power(pu=0.5)
            eut.set_fw({'DbUf': crv.dbof_hz, 'KUf': crv.kof, 'RespTms': crv.tr, 'Pmin': p_min_pu})
            '''
            f) Verify frequency-watt mode is reported as active and that the correct characteristic is reported.
            '''
            dct_steps = self.fwu_traverse_steps(env, eut, crv, af=eut.mra.static.F)
            for k, v in dct_steps.items():
                raise NotImplementedError

    def fwu_validate(self, env: Env, eut: Eut):
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
        # need to apply different validation depending on
        raise NotImplementedError

    def fwu_traverse_steps(self, env: Env, eut: Eut, crv: FW_OF, af):
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
        delta_fsmall = eut.delta_Psmall * eut.fN * crv.kof
        ret = {
            'g': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN - crv.dbof_hz + af),
            'h': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN - crv.dbof_hz - af),
            'i': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN - crv.dbof_hz - delta_fsmall),
            'j': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fL),
            'k': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fL + delta_fsmall),
            'l': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN - crv.dbof_hz - af),
            'm': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN - crv.dbof_hz + af),
            'n': lambda: env.ac_config(rocof=eut.rocof(), freq=eut.fN),
        }
        return ret

