'''
5.4 Test for response to voltage disturbances
'''
import pandas as pd
import enum
from datetime import timedelta
import copy

from pyUL1741SB.IEEE1547.base import IEEE1547Common
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.FreqSupp import FW_OF, FW_UF
from pyUL1741SB import Eut, Env
from pyUL1741SB.eut import VoltShallTripValue


class OpMode(enum.Enum):
    ContOp = 1
    MandOp = 2
    MandOpC = 3  # During this test condition, the EUT may stay in momentary cessation for voltages less than 0.5 p.u. but shall not trip
    MomCess = 4


class LVRTSeq:
    def __init__(self, df_dset1, df_dset2, df_dset3, df_dset4):
        self.df_dsets = [df_dset1, df_dset2, df_dset3, df_dset4]
    @staticmethod
    def AOPCatI():
        raise NotImplementedError
    @staticmethod
    def AOPCatII():
        raise NotImplementedError
    @staticmethod
    def AOPCatIII():
        # 0.88-1.00 for 5s, OpMode.ContOp
        # 0.00-0.05 for 1s, OpMode.MomCess
        # 0.00-0.50 for 9s, OpMode.MandOp
        # 0.50-0.70 for 10s, OpMode.MandOp
        df_dset1 = pd.DataFrame({
            VoltDist.Vminkey: [0.88, 0.00, 0.00, 0.50],
            VoltDist.Vmaxkey: [1.00, 0.05, 0.50, 0.70],
            VoltDist.Durkey: [5, 1, 9, 10],
            VoltDist.OpMdkey: [OpMode.ContOp, OpMode.MomCess, OpMode.MandOpC, OpMode.MandOp]
        })
        # 0.88-1.00 for 5s, OpMode.ContOp
        # 0.00-0.05 for 1s, OpMode.MomCess
        # 0.00-0.50 for 9s, OpMode.MandOp
        # 0.50-0.70 for 10s, OpMode.MandOp
        df_dset2 = pd.DataFrame({
            VoltDist.Vminkey: [0.88, 0.00, 0.00, 0.50],
            VoltDist.Vmaxkey: [1.00, 0.05, 0.50, 0.70],
            VoltDist.Durkey: [5, 1, 9, 10],
            VoltDist.OpMdkey: [OpMode.ContOp, OpMode.MomCess, OpMode.MandOpC, OpMode.MandOp]
        })
        # 0.88-1.00 for 5s, OpMode.ContOp
        # 0.00-0.05 for 1s, OpMode.MomCess
        # 0.00-0.50 for 9s, OpMode.MandOp
        # 0.50-0.70 for 10s, OpMode.MandOp
        # 0.88-1.00 for 120s, OpMode.ContOp
        df_dset3 = pd.DataFrame({
            VoltDist.Vminkey: [0.88, 0.00, 0.00, 0.50, 0.88],
            VoltDist.Vmaxkey: [1.00, 0.05, 0.50, 0.70, 1.00],
            VoltDist.Durkey: [5, 1, 9, 10, 120],
            VoltDist.OpMdkey: [OpMode.ContOp, OpMode.MomCess, OpMode.MandOpC, OpMode.MandOp, OpMode.ContOp]
        })
        # required if restore output capability could not be evaluated in other sequences
        # 0.88-1.00 for 5s, OpMode.ContOp
        # 0.00-0.05 for 1s, OpMode.MomCess
        # 0.52-0.70 for 19s, OpMode.MandOp
        # 0.88-1.00 for 120s, OpMode.ContOp
        df_dset4 = pd.DataFrame({
            VoltDist.Vminkey : [0.88, 0.00, 0.52, 0.88],
            VoltDist.Vmaxkey : [1.00, 0.05, 0.70, 1.00],
            VoltDist.Durkey : [5, 1, 19, 120],
            VoltDist.OpMdkey : [OpMode.ContOp, OpMode.MomCess, OpMode.MandOp, OpMode.ContOp]  # third step is used to eval restore output performance
        })
        return LVRTSeq(df_dset1, df_dset2, df_dset3, df_dset4)

class VoltDist(IEEE1547Common):
    Vminkey = 'Vmin'
    Vmaxkey = 'Vmax'
    Durkey = 'dur_s'
    OpMdkey = 'OpMd'
    def ov_trip_proc(self, env: Env, eut: Eut, pre_cbk=None, post_cbk=None):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError
        shalltrip_tbl = eut.voltshalltrip_tbl
        VN = eut.VN
        vMRA = eut.mra.static.V

        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the EUT.
        '''
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
            for trip_time in trip_times:
                tMRA = eut.mra.static.T(trip_time)
                '''
                i) If the trip magnitude is adjustable, repeat steps e) through h) at the [minimum] maximum of the range.
                '''
                trip_mags = list({trip_region.volt_pu_min, trip_region.volt_pu_max})  # init in set to remove redundant
                for trip_mag in trip_mags:
                    trip_mag = max(trip_mag, (VN + 2 * vMRA) / eut.VN)
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    '''
                    h) For multiphase units, repeat steps e) through g) for the applicable voltage on each phase or phase
                    pair individually, and all phases simultaneously.
                    '''
                    eut.set_vt(**{trip_key: {'vpu': trip_mag, 'cts': trip_time}})
                    for iter in range(5):
                        '''
                        e), f)
                        '''
                        dct_label = {'proc': 'ov', 'region': trip_key, 'time': trip_time, 'mag': trip_mag, 'iter': iter}
                        if pre_cbk is not None:
                            pre_cbk(**dct_label)
                        self.ov_trip_validate(env, eut, dct_label, trip_time, trip_mag, tMRA, vMRA)
                        if post_cbk is not None:
                            post_cbk(**dct_label)
                        self.trip_rst(env, eut)

    def ov_trip_validate(self, env: Env, eut: Eut, dct_label, th, vov, tMRA, vMRA):
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
        env.ac_config(Vac=vov - 2 * vMRA)
        env.sleep(timedelta(seconds=th + 2 * tMRA))
        valid = False
        ts = env.time_now()
        env.ac_config(Vac=vov + 2 * vMRA)
        while not env.elapsed_since(timedelta(seconds=th + 2 * tMRA), ts):
            df_meas = env.meas_single('P', 'Q')
            zipped = zip(df_meas.iloc[0, :].values, [eut.mra.static.P, eut.mra.static.Q])
            if all([v < thresh for v, thresh in zipped]):
                # if eut.state() == Eut.State.FAULT:
                valid = True
                break
        env.validate({**dct_label, 'trip_valid': valid})
        # TODO communication based check for trip state?

    def uv_trip_proc(self, env: Env, eut: Eut):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError
        shalltrip_tbl = eut.voltshalltrip_tbl
        VN = eut.VN
        vMRA = eut.mra.static.V
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all source parameters to the nominal operating conditions for the EUT.
        '''

        '''
        k) Repeat steps c) through j) for each undervoltage operating trip region.
        '''
        '''
        c) Set (or verify) all EUT parameters to the nominal operating settings. If the undervoltage setting is
        adjustable, set the EUT to the maximum undervoltage setting but no greater than the nominal
        voltage minus twice the minimum required accuracy for voltage.
        '''
        for trip_region in [shalltrip_tbl.UV2, shalltrip_tbl.UV1]:
            '''
            d) Set the trip time setting to the minimum.
            '''
            '''
            j) Set the trip time setting to the maximum and repeat steps e) through i).
            '''
            trip_times = list({trip_region.cts_min, trip_region.cts_max})  # init in set to remove redundant
            for trip_time in trip_times:
                '''
                i) If the trip magnitude is adjustable, repeat steps e) through h) at minimum of the range.
                '''
                trip_mags = list({trip_region.volt_pu_min, trip_region.volt_pu_max})  # init in set to remove redundant
                for trip_mag in trip_mags:
                    trip_mag = min(trip_mag, VN - 2 * vMRA)
                    '''
                    h) For multiphase units, repeat steps d) through g) for the applicable voltage on each phase or phase
                    pair individually, and on all phases simultaneously.
                    '''
                    '''
                    g) Repeat steps e) through f) four times for a total of five tests.
                    '''
                    for _ in range(5):
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
                        # TODO
                        tMRA = 0.1
                        self.uv_trip_validate(env, trip_time, trip_mag, tMRA, vMRA)

    def uv_trip_validate(self, env: Env, th, vov, tMRA, vMRA):
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
        env.ac_config(Vac=vov + 2 * vMRA)
        env.sleep(timedelta(th + 2 * tMRA))
        env.ac_config(Vac=vov - 2 * vMRA)
        env.sleep(timedelta(th + 2 * tMRA))
        # TODO wait until trip, up to the trip time setting

    def ovrt_proc(self, env: Env, eut: Eut):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError
        '''
        
        '''
        pass

    def uvrt_proc(self, env: Env, eut: Eut):
        """"""
        multiphase = eut.multiphase
        if multiphase:
            raise NotImplementedError

        if eut.Cat == Eut.Category.A:
            vvcrv = VVCurve.Crv_1A(eut.Prated, eut.VN)
        elif eut.Cat == Eut.Category.B:
            vvcrv = VVCurve.Crv_1B(eut.Prated, eut.VN)
        else:
            raise TypeError(f'unknown category {eut.Cat}')

        if eut.aopCat == Eut.AOPCat.I:
            lvrt_seq = LVRTSeq.AOPCatI()
            fw_of = FW_OF.CatI_CharI()
            fw_uf = FW_UF.CatI_CharI()
        elif eut.aopCat == Eut.AOPCat.II:
            lvrt_seq = LVRTSeq.AOPCatII()
            fw_of = FW_OF.CatII_CharI()
            fw_uf = FW_UF.CatII_CharI()
        elif eut.aopCat == Eut.AOPCat.III:
            lvrt_seq = LVRTSeq.AOPCatIII()
            fw_of = FW_OF.CatIII_CharI()
            fw_uf = FW_UF.CatIII_CharI()
        else:
            raise TypeError(f'unknown category {eut.aopCat}')
        '''
        The settings for magnitude and duration of undervoltage tripping functions shall be
        disabled or set so as not to influence the outcome of the test. 
        The voltage-reactive power control mode of the EUT shall be set to the default settings specified in Table 8 
        of IEEE Std 1547-2018 for the applicable performance category, and enabled. 
        If the EUT provides a voltage-active power control mode, that mode shall be disabled. 
        The frequency-active power control mode of the EUT shall be set to the default settings.
        '''
        # disable uv trip, set vvcrv, disable vw, set vwcrv
        '''
        The ride-through tests shall be performed at two output power levels, high and low, and at any convenient
        power factor greater than 0.90. High power is more than 0.9 of rated, low is between 0.25 to 0.5 of rated
        '''
        PF = 1.0  # 0.9-1.0
        eut.fixed_pf(PF=PF)
        for pwr_pu in [1.0, 0.25]:  # >0.9, 0.25-0.50
            eut.active_power(pu=pwr_pu)
            cond = True
            for df_set in lvrt_seq.df_dsets[:-1]:  # iterate over necessary sets
                self.uvrt_validate(env, eut, df_set)
                cond = True  # TODO required if restore output capability could not be evaluated in other sequences
            if cond:
                df_set = lvrt_seq.df_dsets[-1]
                self.uvrt_validate(env, eut, df_set)

    def uvrt_validate(self, env: Env, eut: Eut, df_set):
        """"""
        '''
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
        for _, row in df_set.iterrows():
            vpu = (row[self.Vminkey] + row[self.Vmaxkey]) / 2
            dur = row[self.Durkey]
            opmd = row[self.OpMdkey]
            env.ac_config(Vac=vpu*eut.VN)
            # wait dur duration
            # eut behavior match opmd
            # TODO
