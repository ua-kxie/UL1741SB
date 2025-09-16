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
        # chars = char1, char2, char1 with Pmin if needed
        pwrs_pu = [1.0, 0.2, 0.66]
        for crv in fw_crvs:
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
                '''
                h) Begin the adjustment to fH. Ramp the frequency to af below (fN + dbOF).
                i) Ramp the frequency to af above (fN + dbOF).
                j) Ramp the frequency to Δfsmall+ fN + dbOF.
                k) Ramp the frequency to fH.
                l) Begin the adjustment back to fN. Ramp the frequency to fH – Δfsmall.
                m) Ramp the frequency to af above (fN + dbOF).
                n) Ramp the frequency to af below (fN + dbOF).
                o) Ramp the frequency to fN.
                '''
                raise NotImplementedError

    def fwu_proc(self, env: Env, eut: Eut):
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all frequency trip parameters to the widest range of adjustability. Disable all reactive/active
        power control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        d) Adjust the EUT’s available active power to Prated. Set the EUT’s output power to 50% of Prated.
        e) Set EUT frequency-watt parameters to the values specified by Characteristic 1. All other functions
        should be turned off.
        f) Verify frequency-watt mode is reported as active and that the correct characteristic is reported.
        g) Begin the adjustment to fL. Ramp the frequency to af above (fN – dbUF).
        h) Ramp the frequency to af below (fN – dbUF).
        i) Ramp the frequency to fN − Δfsmall – dbUF.
        j) Ramp the frequency to fL.
        k) Begin the adjustment back to fN. Ramp the frequency to fL + Δfsmall.
        l) Ramp the frequency to af below (fN – dbUF).
        m) Ramp the frequency to af above (fN – dbUF).
        n) Ramp the frequency to fN.
        o) Repeat steps b) through n) for Characteristic 2.
        p) For EUTs that can absorb power, rerun Characteristic 1 allowing the unit to absorb power by
        programming a negative Pmin. Set the unit to absorb power at −50% of Prated.
        '''