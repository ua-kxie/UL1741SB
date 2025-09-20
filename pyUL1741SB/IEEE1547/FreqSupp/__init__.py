"""
IEEE 1547.1-2020 5.15
"""
from pyUL1741SB import Eut, Env

class FW_OF:
    def __init__(self, dbof_hz, kof, tr):
        self.dbof_hz = dbof_hz
        self.kof = kof
        self.tr = tr

    @staticmethod
    def CatI_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatII_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatIII_CharI(): return FW_OF(dbof_hz=0.036, kof=0.05, tr=5)
    @staticmethod
    def CatI_CharII(): return FW_OF(dbof_hz=0.017, kof=0.03, tr=1)
    @staticmethod
    def CatII_CharII(): return FW_OF(dbof_hz=0.017, kof=0.03, tr=1)
    @staticmethod
    def CatIII_CharII(): return FW_OF(dbof_hz=0.017, kof=0.02, tr=0.2)

class FW_UF:
    def __init__(self, dbuf_hz, kuf, tr):
        self.dbuf_hz = dbuf_hz
        self.kuf = kuf
        self.tr = tr

    @staticmethod
    def CatI_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatII_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatIII_CharI(): return FW_UF(dbuf_hz=0.036, kuf=0.05, tr=5)
    @staticmethod
    def CatI_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatII_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.03, tr=1)
    @staticmethod
    def CatIII_CharII(): return FW_UF(dbuf_hz=0.017, kuf=0.02, tr=0.2)

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
class FW:
    def fwo_proc(self, env: Env, eut: Eut):
        """"""
        # chars = char1, char2, char1 with Pmin if needed
        fw_crvs = {
            Eut.AOPCat.I: [FW_OF.CatI_CharI(), FW_OF.CatI_CharII(), FW_OF.CatI_CharI()],
            Eut.AOPCat.II: [FW_OF.CatII_CharI(), FW_OF.CatII_CharII(), FW_OF.CatII_CharI()],
            Eut.AOPCat.III: [FW_OF.CatIII_CharI(), FW_OF.CatIII_CharII(), FW_OF.CatIII_CharI()],
        }[eut.aopCat]
        p_mins_pu = [eut.Pmin/eut.Prated, eut.Pmin/eut.Prated, eut.Pmin_prime/eut.Prated]
        fw_crvs = list(zip(fw_crvs, p_mins_pu))
        if not eut.Pmin_prime < 0:
            # discard second CharI run if eut can not absorb active power
            fw_crvs = fw_crvs[:-1]
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
        for crv, p_min_pu in fw_crvs:
            eut.set_fw({'DbOf': crv.dbof_hz, 'KOf':crv.kof, 'RespTms': crv.tr, 'Pmin': p_min_pu})
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
                dct_steps = self.fwo_traverse_steps(env, eut, crv, af=eut.mra.static.F)
                for k, v in dct_steps.items():
                    self.fwo_validate(env, eut)

    def fwo_validate(self, env: Env, eut: Eut):
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
        # need to apply different validation depending on
        raise NotImplementedError

    def fwo_traverse_steps(self, env: Env, eut: Eut, crv: FW_OF, af):
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

