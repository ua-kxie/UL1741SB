from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable
import opender as der

class EpriEut(Eut):
    def __init__(self, **kwargs):
        self.der = der.DER()
        self.der.der_file.NP_PHASE = "SINGLE"
        self.der.update_der_input(v_pu=1, f=60, p_dc_pu=1.0)
        self.der.run()
        super().__init__(
            Cat=Eut.Category.B,
            aopCat=Eut.AOPCat.III,
            voltshalltrip_tbl=VoltShallTripTable.AOPCatIII(240),
            freqshalltrip_tbl=FreqShallTripTable.MaxRange(),
            vfo=False,
            Prated=self.der.der_file.NP_P_MAX,
            Prated_prime=0,
            Srated=self.der.der_file.NP_P_MAX,
            Vin_nom=self.der.der_file.NP_V_DC,
            Vin_min=None,
            Vin_max=None,
            VN=self.der.der_file.NP_AC_V_NOM,
            VL=self.der.der_file.NP_AC_V_NOM * 0.9,
            VH=self.der.der_file.NP_AC_V_NOM * 1.1,
            Pmin=0,
            Pmin_prime=0,
            Qrated_abs=self.der.der_file.NP_Q_MAX_ABS,
            Qrated_inj=-self.der.der_file.NP_Q_MAX_INJ,
            Comms=[Eut.Comms.SUNS],
            multiphase=False,
            fL=59.0,  # minimum frequency in continuous operating region (Hz)
            fN=60.0,  # nominal frequency (Hz)
            fH=61.0,  # maximum frequency in continuous operating region (Hz)
            delta_Psmall=0.1,  # small power change threshold (p.u.)
            delta_Plarge=0.5  # large power change threshold (p.u.)
        )

    def fixed_pf(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                self.der.der_file.CONST_PF_MODE_ENABLE = v
            elif k == 'PF':
                if v < 0:
                    self.der.der_file.CONST_PF_EXCITATION = 'ABS'
                    self.der.der_file.CONST_PF = -v
                else:
                    self.der.der_file.CONST_PF_EXCITATION = 'INJ'
                    self.der.der_file.CONST_PF = v
            else:
                raise NotImplementedError

    def wlim(self, Ena: bool, pu):
        self.der.der_file.AP_LIMIT_ENABLE = Ena
        self.der.der_file.AP_LIMIT = pu

    def active_power(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'pu':
                self.der.update_der_input(p_dc_pu=v)
            else:
                raise NotImplementedError

    def reactive_power(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                self.der.der_file.CONST_Q_MODE_ENABLE = v
            elif k == 'Q':
                self.der.der_file.CONST_Q = v / self.der.der_file.NP_VA_MAX
            else:
                raise NotImplementedError

    def set_vv(self, Ena: bool, crv: VVCurve=None):
        self.der.der_file.QV_MODE_ENABLE = Ena
        if crv is not None:
            self.der.der_file.QV_CURVE_Q1 = crv.Q1
            self.der.der_file.QV_CURVE_Q2 = crv.Q2
            self.der.der_file.QV_CURVE_Q3 = crv.Q3
            self.der.der_file.QV_CURVE_Q4 = crv.Q4
            self.der.der_file.QV_CURVE_V1 = crv.V1
            self.der.der_file.QV_CURVE_V2 = crv.V2
            self.der.der_file.QV_CURVE_V3 = crv.V3
            self.der.der_file.QV_CURVE_V4 = crv.V4
            self.der.der_file.QV_OLRT = crv.Tr

    def set_wv(self, Ena: bool, crv: WVCurve=None):
        self.der.der_file.QP_MODE_ENABLE = Ena
        if crv is not None:
            self.der.der_file.QP_CURVE_Q1_GEN = crv.Q1
            self.der.der_file.QP_CURVE_Q2_GEN = crv.Q2
            self.der.der_file.QP_CURVE_Q3_GEN = crv.Q3
            self.der.der_file.QP_CURVE_P1_GEN = crv.P1
            self.der.der_file.QP_CURVE_P2_GEN = crv.P2
            self.der.der_file.QP_CURVE_P3_GEN = crv.P3
            self.der.der_file.QP_CURVE_Q1_LOAD = crv.Q1_prime
            self.der.der_file.QP_CURVE_Q2_LOAD = crv.Q2_prime
            self.der.der_file.QP_CURVE_Q3_LOAD = crv.Q3_prime
            self.der.der_file.QP_CURVE_P1_LOAD = crv.P1_prime
            self.der.der_file.QP_CURVE_P2_LOAD = crv.P2_prime
            self.der.der_file.QP_CURVE_P3_LOAD = crv.P3_prime

    def set_vw(self, Ena: bool, crv: VWCurve=None):
        self.der.der_file.PV_MODE_ENABLE = Ena
        if crv is not None:
            self.der.der_file.PV_CURVE_P1 = crv.P1
            self.der.der_file.PV_CURVE_P2 = crv.P2
            self.der.der_file.PV_CURVE_V1 = crv.V1
            self.der.der_file.PV_CURVE_V2 = crv.V2
            self.der.der_file.PV_OLRT = crv.Tr

    def set_vv_vref(self, Ena: bool, Tref_s):
        self.der.der_file.QV_VREF_AUTO_MODE = Ena
        self.der.der_file.QV_VREF_TIME = Tref_s

    def set_vt(self, **kwargs):
        """
        :param kwargs: OV2, OV1, UV1, UV2, each is a dict of {'vpu': trip_mag, 'cts': trip_time}
        :return:
        """
        for k, v in kwargs.items():
            if k == 'OV2':
                self.der.der_file.OV2_TRIP_V = v['vpu']
                self.der.der_file.OV2_TRIP_T = v['cts']
            elif k == 'OV1':
                self.der.der_file.OV1_TRIP_V = v['vpu']
                self.der.der_file.OV1_TRIP_T = v['cts']
            elif k == 'UV1':
                self.der.der_file.UV1_TRIP_V = v['vpu']
                self.der.der_file.UV1_TRIP_T = v['cts']
            elif k == 'UV2':
                self.der.der_file.UV2_TRIP_V = v['vpu']
                self.der.der_file.UV2_TRIP_T = v['cts']
            else:
                raise NotImplementedError

    def set_ft(self, **kwargs):
        """
        :param kwargs: OF2, OF1, UF1, UF2, each is a dict of {'vpu': trip_mag, 'cts': trip_time}
        :return:
        """
        for k, v in kwargs.items():
            if k == 'OF2':
                self.der.der_file.OF2_TRIP_F = v['freq']
                self.der.der_file.OF2_TRIP_T = v['cts']
            elif k == 'OF1':
                self.der.der_file.OF1_TRIP_F = v['freq']
                self.der.der_file.OF1_TRIP_T = v['cts']
            elif k == 'UF1':
                self.der.der_file.UF1_TRIP_F = v['freq']
                self.der.der_file.UF1_TRIP_T = v['cts']
            elif k == 'UF2':
                self.der.der_file.UF2_TRIP_F = v['freq']
                self.der.der_file.UF2_TRIP_T = v['cts']
            else:
                raise NotImplementedError

    def has_tripped(self):
        return self.der.der_status == 'Trip'

    def set_fw(self, Ena: bool, crv: FWChar=None):
        """
        :param kwargs: Ena, DbOf, DbUf, KOf, KUf, RespTms, PMin
        :return:
        """
        self.der.der_file.PF_MODE_ENABLE = Ena
        self.der.der_file.PF_DBOF = crv.dbof_hz
        self.der.der_file.PF_DBUF = crv.dbuf_hz
        self.der.der_file.PF_KOF = crv.kof
        self.der.der_file.PF_KUF = crv.kuf
        self.der.der_file.PF_OLRT = crv.tr
        self.der.der_file.NP_P_MIN_PU = 0

