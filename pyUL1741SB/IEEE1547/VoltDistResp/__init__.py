'''
5.4 Test for response to voltage disturbances
'''
import pandas as pd
import enum
from datetime import timedelta
import copy

from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB import Eut, Env


"""
IEEE 1547.1-2020
4.5 Cease to energize performance requirement
In the cease to energize state, the DER shall not deliver active power during steady-state or transient
conditions. The requirements for cease to energize shall apply to the point of DER connection (PoC).
For Local EPS with aggregate DER rating less than 500 kVA, the reactive power exchange in the cease to
energize state shall be less than 10% of nameplate DER rating and shall exclusively result from passive
devices. For Local EPS with aggregate DER rating 500 kVA and greater, the reactive power exchange in
the cease to energize state shall be less than 3% of nameplate DER rating and shall exclusively result from
passive devices.

shall not deliver active power
reactive power limited to 3 (10) % for DER rated less (more) than 500kVA
"""

class OpMode(enum.Enum):
    ContOp = 1
    MandOp = 2
    MandOpC = 3  # During this test condition, the EUT may stay in momentary cessation for voltages less than 0.5 p.u. but shall not trip
    MomCess = 4

class CondName(enum.Enum):
    A = 1
    B = 2
    C = 3
    Cprime = 4
    D = 5
    E = 6
    F = 7

class VrtCond:
    def __init__(self, name: CondName, vpu, vpu_min, vpu_max, dur_s, opmd: OpMode):
        self.name = name
        self.vpu = vpu
        self.vpu_min = vpu_min
        self.vpu_max = vpu_max
        self.dur_s = dur_s
        self.opmd = opmd

    @staticmethod
    def catIII_lvrt_condA():
        return VrtCond(name=CondName.A, vpu=0.88, vpu_min=0.88, vpu_max=1.0, dur_s=5.0, opmd=OpMode.ContOp)

    @staticmethod
    def catIII_lvrt_condB():
        return VrtCond(name=CondName.B, vpu=0.02, vpu_min=0.0, vpu_max=0.05, dur_s=1.0, opmd=OpMode.MomCess)

    @staticmethod
    def catIII_lvrt_condC():
        return VrtCond(name=CondName.C, vpu=0.48, vpu_min=0.0, vpu_max=0.5, dur_s=9.0, opmd=OpMode.MandOpC)

    @staticmethod
    def catIII_lvrt_condCprime():
        return VrtCond(name=CondName.Cprime, vpu=0.52, vpu_min=0.52, vpu_max=0.7, dur_s=9.0, opmd=OpMode.MandOp)

    @staticmethod
    def catIII_lvrt_condD():
        return VrtCond(name=CondName.D, vpu=0.52, vpu_min=0.5, vpu_max=0.7, dur_s=10.0, opmd=OpMode.MandOp)

    @staticmethod
    def catIII_lvrt_condE():
        return VrtCond(name=CondName.E, vpu=0.88, vpu_min=0.88, vpu_max=1.00, dur_s=120.0, opmd=OpMode.ContOp)

    @staticmethod
    def catIII_hvrt_condA():
        return VrtCond(name=CondName.A, vpu=1.1, vpu_min=1.0, vpu_max=1.1, dur_s=5.0, opmd=OpMode.ContOp)

    @staticmethod
    def catIII_hvrt_condB():
        return VrtCond(name=CondName.B, vpu=1.18, vpu_min=1.18, vpu_max=1.2, dur_s=12.0, opmd=OpMode.MomCess)

    @staticmethod
    def catIII_hvrt_condBprime():
        return VrtCond(name=CondName.Cprime, vpu=1.12, vpu_min=1.12, vpu_max=1.2, dur_s=12.0, opmd=OpMode.MomCess)

    @staticmethod
    def catIII_hvrt_condC():
        return VrtCond(name=CondName.D, vpu=1.1, vpu_min=1.0, vpu_max=1.1, dur_s=120.0, opmd=OpMode.ContOp)

class VoltDist(IEEE1547):
    Vminkey = 'Vmin'
    Vmaxkey = 'Vmax'
    Durkey = 'dur_s'
    OpMdkey = 'OpMd'
    def ovt_proc(self):
        """"""
        multiphase = self.c_eut.multiphase
        if multiphase:
            raise NotImplementedError
        shalltrip_tbl = self.c_eut.voltshalltrip_tbl
        VN = self.c_eut.VN
        vMRA = self.c_eut.mra.static.V
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the eut.
        '''
        self.conn_to_grid()
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        '''
        k) Repeat steps c) through k) for each overvoltage operating trip region.
        '''
        for trip_key, trip_region in {'OV2': shalltrip_tbl.OV2, 'OV1': shalltrip_tbl.OV1}.items():
            '''
            c) Set (or verify) all EUT parameters to the nominal operating settings. If the overvoltage setting is
            adjustable, set the EUT to the minimum overvoltage setting, but no less than the nominal voltage
            plus twice the minimum required accuracy for voltage.
            d) Set the trip time setting to the minimum.
            '''
            '''
            j) Set the trip time setting to the maximum and repeat steps e) through i).
            '''
            trip_times = list({trip_region.cts_min, trip_region.cts_max})  # init in set to remove redundant
            for trip_cts in trip_times:
                '''
                i) If the trip magnitude is adjustable, repeat steps e) through h) at the [minimum] maximum of the range.
                '''
                trip_mags = list({trip_region.volt_pu_min, trip_region.volt_pu_max})  # init in set to remove redundant
                for trip_vpu in trip_mags:
                    trip_vpu = max(trip_vpu, (VN + 2 * vMRA) / VN)
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    '''
                    h) For multiphase units, repeat steps e) through g) for the applicable voltage on each phase or phase
                    pair individually, and all phases simultaneously.
                    '''
                    self.c_eut.set_vt(**{trip_key: {'vpu': trip_vpu, 'cts': trip_cts}})
                    for i in range(self.trip_rpt):
                        '''
                        e), f)
                        '''
                        dct_label = {'proc': 'ovt', 'region': trip_key, 'time': trip_cts, 'mag': trip_vpu, 'iter': i}
                        self.ovt_validate(dct_label, trip_cts, trip_vpu)
                        self.trip_rst()

    def ovt_validate(self, dct_label, trip_cts, trip_vpu):
        """"""
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

        5.4.2.4 Criteria
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within
        respective clearing times for each overvoltage range specified in IEEE Std 1547. The evaluated ranges of
        adjustment for tripping magnitude and duration shall be greater than or equal to the allowable ranges of
        adjustment for each overvoltage tripping range specified in IEEE Std 1547.
        
        A.3 Notes:
        (a) Where the parameter under test is voltage, the rise times shall be as fast as possible and
        shall not exceed 2 cycles.
        (b) The hold time, th, shall be greater than or equal to 100% of the trip time setting plus 200%
        the minimum required measurement accuracy (MRA) for time, as specified in Table 3 of
        IEEE Std 1547-2018 for steady-state conditions.
        (c) The clearing time shall be measured from the time t0 to tc.
        '''
        tMRA = self.c_eut.mra.static.T(trip_cts)
        vMRA = self.c_eut.mra.static.V
        dur = timedelta(seconds=trip_cts + 2 * tMRA)
        step0 = lambda: self.c_env.ac_config(Vac=trip_vpu * self.c_eut.VN - 2 * vMRA)
        step1 = lambda: self.c_env.ac_config(Vac=trip_vpu * self.c_eut.VN + 2 * vMRA)
        meas_args = ('P', 'Q', 'V')
        self.trip_step(dct_label, dur, tMRA, step0, step1, meas_args)

    def uvt_proc(self):
        """"""
        multiphase = self.c_eut.multiphase
        if multiphase:
            raise NotImplementedError
        shalltrip_tbl = self.c_eut.voltshalltrip_tbl
        VN = self.c_eut.VN
        vMRA = self.c_eut.mra.static.V
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the eut.
        '''
        self.conn_to_grid()
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        '''
        k) Repeat steps c) through j) for each undervoltage operating trip region.
        '''
        '''
        c) Set (or verify) all EUT parameters to the nominal operating settings. If the undervoltage setting is
        adjustable, set the EUT to the maximum undervoltage setting but no greater than the nominal
        voltage minus twice the minimum required accuracy for voltage.
        '''
        for trip_key, trip_region in {'UV2': shalltrip_tbl.UV2, 'UV1': shalltrip_tbl.UV1}.items():
            '''
            d) Set the trip time setting to the minimum.
            '''
            '''
            j) Set the trip time setting to the maximum and repeat steps e) through i).
            '''
            trip_times = list({trip_region.cts_min, trip_region.cts_max})  # init in set to remove redundant
            for trip_cts in trip_times:
                '''
                i) If the trip magnitude is adjustable, repeat steps e) through h) at minimum of the range.
                '''
                trip_mags = list({trip_region.volt_pu_min, trip_region.volt_pu_max})  # init in set to remove redundant
                for trip_vpu in trip_mags:
                    trip_vpu = min(trip_vpu, (VN - 2 * vMRA) / VN)
                    '''
                    h) For multiphase units, repeat steps d) through g) for the applicable voltage on each phase or phase
                    pair individually, and on all phases simultaneously.
                    '''
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    self.c_eut.set_vt(**{trip_key: {'vpu': trip_vpu, 'cts': trip_cts}})
                    for i in range(self.trip_rpt):
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
                        dct_label = {'proc': 'uvt', 'region': trip_key, 'time': trip_cts, 'mag': trip_vpu, 'iter': i}
                        self.uvt_validate(dct_label, trip_cts, trip_vpu)
                        self.trip_rst()

    def uvt_validate(self, dct_label, trip_cts, trip_vpu):
        """"""
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

        5.4.3.4 Criteria
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within the
        respective clearing times for each undervoltage tripping range specified in IEEE Std 1547. The evaluated
        ranges of adjustment for tripping magnitude and duration shall be greater than or equal to the allowable
        ranges of adjustment for each undervoltage tripping range specified in IEEE Std 1547.
        '''
        tMRA = self.c_eut.mra.static.T(trip_cts)
        vMRA = self.c_eut.mra.static.V
        dur = timedelta(seconds=trip_cts + 2 * tMRA)
        step0 = lambda: self.c_env.ac_config(Vac=trip_vpu * self.c_eut.VN + 2 * vMRA)
        step1 = lambda: self.c_env.ac_config(Vac=max(0, trip_vpu * self.c_eut.VN - 2 * vMRA))
        meas_args = ('P', 'Q', 'V')
        self.trip_step(dct_label, dur, tMRA, step0, step1, meas_args)

    def lvrt_proc(self):
        """"""
        multiphase = self.c_eut.multiphase
        if multiphase:
            raise NotImplementedError

        if self.c_eut.Cat == self.c_eut.Category.A:
            vvcrv = VVCurve.Crv_1A()
        elif self.c_eut.Cat == self.c_eut.Category.B:
            vvcrv = VVCurve.Crv_1B()
        else:
            raise ValueError(self.c_eut.Cat)

        if self.c_eut.aopCat == self.c_eut.AOPCat.I:
            fwchar = FWChar.CatI_CharI()
            raise NotImplementedError
        elif self.c_eut.aopCat == self.c_eut.AOPCat.II:
            fwchar = FWChar.CatII_CharI()
            raise NotImplementedError
        elif self.c_eut.aopCat == self.c_eut.AOPCat.III:
            fwchar = FWChar.CatIII_CharI()
            seq = [
                VrtCond.catIII_lvrt_condA(), VrtCond.catIII_lvrt_condB(), VrtCond.catIII_lvrt_condC(), VrtCond.catIII_lvrt_condD(),
                VrtCond.catIII_lvrt_condA(), VrtCond.catIII_lvrt_condB(), VrtCond.catIII_lvrt_condC(), VrtCond.catIII_lvrt_condD(),
                VrtCond.catIII_lvrt_condA(), VrtCond.catIII_lvrt_condB(), VrtCond.catIII_lvrt_condC(), VrtCond.catIII_lvrt_condD(), VrtCond.catIII_lvrt_condE(),
                VrtCond.catIII_lvrt_condA(), VrtCond.catIII_lvrt_condB(), VrtCond.catIII_lvrt_condCprime(), VrtCond.catIII_lvrt_condD(), VrtCond.catIII_lvrt_condE(),
            ]
        else:
            raise ValueError(self.c_eut.Cat)
        resptm = timedelta(seconds=VrtCond.catIII_lvrt_condB().dur_s)
        vt_tbl = self.c_eut.voltshalltrip_tbl
        vt_args = {
            'UV1': {'cts': vt_tbl.UV1.cts_max, 'vpu': vt_tbl.UV1.volt_pu_min},
            'UV2': {'cts': vt_tbl.UV2.cts_max, 'vpu': vt_tbl.UV2.volt_pu_min}
        }
        '''
        The settings for magnitude and duration of undervoltage tripping functions shall be
        disabled or set so as not to influence the outcome of the test. 
        The voltage-reactive power control mode of the EUT shall be set to the default settings specified in Table 8 
        of IEEE Std 1547-2018 for the applicable performance category, and enabled. 
        If the EUT provides a voltage-active power control mode, that mode shall be disabled. 
        The frequency-active power control mode of the EUT shall be set to the default settings.
        '''
        self.conn_to_grid()
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.set_vt(**vt_args)
        self.c_eut.set_vv(Ena=True, crv=vvcrv)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_fw(Ena=True, crv=fwchar)
        '''
        The ride-through tests shall be performed at two output power levels, high and low, and at any convenient
        power factor greater than 0.90. High power is more than 0.9 of rated, low is between 0.25 to 0.5 of rated
        '''
        PF = 1.0  # 0.9-1.0
        self.c_eut.set_cpf(PF=PF)
        for pwr_pu in [1.0, 0.25]:  # >0.9, 0.25-0.50
            self.c_eut.set_ap(Ena=True, pu=pwr_pu)
            for cond in seq:
                dct_label = {
                    'proc': 'lvrt',
                    'pwr_pu': pwr_pu,
                    'cond': str(cond.name)
                }
                self.lvrt_validate(dct_label, resptm, cond)

    def lvrt_validate(self, dct_label, resptm: timedelta, cond: VrtCond):
        """"""
        '''
        IEEE 1547.1-2020 5.4.4.5
        Where the operating mode is specified as Mandatory Operation, the EUT shall not trip, shall
        maintain synchronism and maintain its total apparent current during the disturbance period at or
        above 80% of the pre-disturbance value.
        
        Where the operating mode is specified as Permissive Operation, the EUT may Cease to Energize
        followed by Restore Output, or may continue to exchange current with the ac test source. The EUT
        shall ride through and shall not trip during Permissive Operation. Where the EUT rides through in
        a Cease to Energize state, the EUT shall comply with the Restore Output requirements in 6.4.2.7 of
        IEEE Std 1547-2018.
        
        Where the operating mode is specified as Momentary Cessation, the EUT shall cease to energize
        the ac test source. Following the momentary cessation event, the EUT shall comply with the
        Restore Output requirements of 6.4.2.7 of IEEE Std 1547-2018.
        '''
        meas_args = ('V', 'P', 'Q')
        ntrvl = timedelta(seconds=cond.dur_s)
        def perturb():
            self.c_env.ac_config(Vac=cond.vpu * self.c_eut.VN)
        df_meas = self.meas_perturb(perturb, ntrvl, ntrvl, meas_args)
        resp_idx = df_meas.index.asof(df_meas.index[0] + resptm)

        def contop_valid():
            s = ((df_meas.loc[resp_idx:, 'P'] ** 2 + df_meas.loc[:, 'Q'] ** 2) ** 0.5).mean()
            v = df_meas.loc[resp_idx:, 'V'].mean()
            self.predist_apparent_current = s/v
            return s > self.c_eut.mra.static.P * self.mra_scale  # ap is subject to vv-modulation due to Srated

        def momcess_valid():
            p = df_meas.loc[resp_idx:, 'P'].mean()  # response time not specified, just going to use mean
            q = df_meas.loc[resp_idx:, 'Q'].mean()
            p_thresh = 0.01 * self.c_eut.Srated / self.c_eut.VN  # not explicitly stipulated, just says shall not deliver AP to grid
            q_thresh = 0.1 * self.c_eut.Srated if self.c_eut.Srated < 500e3 else 0.03 * self.c_eut.Srated # IEEE 1547.1-2018 4.5
            return p < p_thresh and q < q_thresh

        def mandop_valid():
            s = ((df_meas.loc[resp_idx:, 'P'] ** 2 + df_meas.loc[resp_idx:, 'Q'] ** 2) ** 0.5).mean()
            v = df_meas.loc[resp_idx:, 'V'].mean()
            return (s / v) > (0.8 * self.predist_apparent_current)

        if cond.opmd == OpMode.ContOp:
            valid = contop_valid()
            self.prev_st = OpMode.ContOp
        elif cond.opmd == OpMode.MomCess:
            valid = momcess_valid()
            self.prev_st = OpMode.MomCess
        elif cond.opmd == OpMode.MandOpC:
            momcess_valid = momcess_valid()
            mandop_valid = mandop_valid()
            valid = (momcess_valid and self.prev_st == OpMode.MomCess) or mandop_valid
            self.prev_st = OpMode.MandOp
        elif cond.opmd == OpMode.MandOp:
            valid = mandop_valid()
            self.prev_st = OpMode.MandOp
        else:
            raise ValueError(cond.opmd)

        self.c_env.validate(dct_label={
            **dct_label,
            'valid': valid,
            'data': df_meas
        })

    def hvrt_proc(self):
        """"""
        multiphase = self.c_eut.multiphase
        if multiphase:
            raise NotImplementedError

        if self.c_eut.Cat == self.c_eut.Category.A:
            vvcrv = VVCurve.Crv_1A()
        elif self.c_eut.Cat == self.c_eut.Category.B:
            vvcrv = VVCurve.Crv_1B()
        else:
            raise ValueError(self.c_eut.Cat)

        if self.c_eut.aopCat == self.c_eut.AOPCat.I:
            raise NotImplementedError
        elif self.c_eut.aopCat == self.c_eut.AOPCat.II:
            raise NotImplementedError
        elif self.c_eut.aopCat == self.c_eut.AOPCat.III:
            seq = [
                VrtCond.catIII_hvrt_condA(), VrtCond.catIII_hvrt_condB(),
                VrtCond.catIII_hvrt_condA(), VrtCond.catIII_hvrt_condB(),
                VrtCond.catIII_hvrt_condA(), VrtCond.catIII_hvrt_condB(), VrtCond.catIII_hvrt_condC(),
                VrtCond.catIII_hvrt_condA(), VrtCond.catIII_hvrt_condBprime(), VrtCond.catIII_hvrt_condC(),
            ]
        else:
            raise ValueError(self.c_eut.Cat)
        resptm = timedelta(seconds=VrtCond.catIII_lvrt_condB().dur_s)
        vt_tbl = self.c_eut.voltshalltrip_tbl
        vt_args = {
            'UV1': {'cts': vt_tbl.UV1.cts_max, 'vpu': vt_tbl.UV1.volt_pu_min},
            'UV2': {'cts': vt_tbl.UV2.cts_max, 'vpu': vt_tbl.UV2.volt_pu_min}
        }
        '''
        The voltage-reactive power control mode of the EUT shall be set to the default settings specified in Table 8
        of IEEE Std 1547-2018 for the applicable performance category, and enabled.
        '''
        self.conn_to_grid()
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.set_vv(Ena=True, crv=vvcrv)
        self.c_eut.set_vw(Ena=False)  # not specified but helps identify cont.op
        '''
        The ride-through tests shall be performed at two output power levels, high and low, and at any convenient
        power factor greater than 0.90. High power is more than 0.9 of rated, low is between 0.25 to 0.5 of rated
        '''
        PF = 1.0  # 0.9-1.0
        self.c_eut.set_cpf(PF=PF)
        for pwr_pu in [1.0, 0.25]:  # >0.9, 0.25-0.50
            self.c_eut.set_ap(Ena=True, pu=pwr_pu)
            for cond in seq:
                dct_label = {
                    'proc': 'hvrt',
                    'pwr_pu': pwr_pu,
                    'cond': str(cond.name)
                }
                self.hvrt_validate(dct_label, resptm, cond)

    def hvrt_validate(self, dct_label, resptm: timedelta, cond: VrtCond):
        """"""
        '''
        IEEE 1547.1-2020 5.4.7.6
        Where the operating mode is specified as Permissive Operation, the EUT may Cease to Energize or may
        continue to exchange current with the ac test source. The EUT shall ride through and shall not trip during
        Permissive Operation. If the operating mode of the EUT during Permissive Operation is Cease to Energize,
        the EUT shall comply with the Restore Output requirements 6.4.2.7 of IEEE Std 1547-2018.
        
        Where the operating mode is specified as Momentary Cessation, the EUT shall cease to exchange current
        with the resistive load bank or ac test source. Following the momentary cessation event the EUT shall
        comply with the Restore Output requirements of 6.4.2.7 of IEEE Std 1547-2018.
        '''
        meas_args = ('V', 'P', 'Q')
        ntrvl = timedelta(seconds=cond.dur_s)

        def perturb():
            self.c_env.ac_config(Vac=cond.vpu * self.c_eut.VN)

        df_meas = self.meas_perturb(perturb, ntrvl, ntrvl, meas_args)
        resp_idx = df_meas.index.asof(df_meas.index[0] + resptm)

        def contop_valid():
            s = ((df_meas.loc[resp_idx:, 'P'] ** 2 + df_meas.loc[:, 'Q'] ** 2) ** 0.5).mean()
            v = df_meas.loc[resp_idx:, 'V'].mean()
            self.predist_apparent_current = s/v
            return s > self.c_eut.mra.static.P * self.mra_scale  # ap is subject to vv-modulation due to Srated

        def momcess_valid():
            p = df_meas.loc[resp_idx:, 'P'].mean()  # response time not specified, just going to use mean
            q = df_meas.loc[resp_idx:, 'Q'].mean()
            p_thresh = 0.01 * self.c_eut.Srated / self.c_eut.VN  # not explicitly stipulated, just says shall not deliver AP to grid
            q_thresh = 0.1 * self.c_eut.Srated if self.c_eut.Srated < 500e3 else 0.03 * self.c_eut.Srated # IEEE 1547.1-2018 4.5
            return p < p_thresh and q < q_thresh

        if cond.opmd == OpMode.ContOp:
            valid = contop_valid()
        elif cond.opmd == OpMode.MomCess:
            valid = momcess_valid()
        else:
            raise ValueError(cond.opmd)

        self.c_env.validate(dct_label={
            **dct_label,
            'valid': valid,
            'data': df_meas
        })
