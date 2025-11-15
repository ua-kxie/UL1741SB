from ctypes import *
from pyUL1741SB import Eut
from pyUL1741SB.eut import VoltShallTripTable, FreqShallTripTable

# Load DLL
derc = CDLL('tests/derc/derc.dll')

# Structures matching derc.h
class CrvPt(Structure):
    _fields_ = [('x', c_float), ('y', c_float)]

class VoltVarCrv(Structure):
    _fields_ = [('pts', CrvPt * 4)]

class WattVarCrv(Structure):
    _fields_ = [('pts', CrvPt * 6)]

class VoltWattCrv(Structure):
    _fields_ = [('pts', CrvPt * 2)]

class TripPt(Structure):
    _fields_ = [('mag', c_float), ('cts', c_float)]

class VoltTrips(Structure):
    _fields_ = [
        ('ov1', TripPt), ('ov2', TripPt),
        ('uv1', TripPt), ('uv2', TripPt)
    ]

class FreqTrips(Structure):
    _fields_ = [
        ('of1', TripPt), ('of2', TripPt),
        ('uf1', TripPt), ('uf2', TripPt)
    ]

class ESCfg(Structure):
    _fields_ = [
        ('ena', c_int), ('ov', c_float), ('uv', c_float),
        ('of', c_float), ('uf', c_float), ('delay', c_float), ('ramp_time', c_float)
    ]

class FWCfg(Structure):
    _fields_ = [
        ('of', c_float * 2), ('uf', c_float * 2), ('ena', c_int), ('olrt', c_float)
    ]

class VWCfg(Structure):
    _fields_ = [('ena', c_int), ('crv', VoltWattCrv), ('olrt', c_float)]

class LAPCfg(Structure):
    _fields_ = [('ena', c_int), ('ap', c_float)]

class CPFCfg(Structure):
    _fields_ = [('ena', c_int), ('pf', c_float), ('exct', c_int)]

class CRPCfg(Structure):
    _fields_ = [('ena', c_int), ('var', c_float)]

class VVCfg(Structure):
    _fields_ = [
        ('ena', c_int), ('vref', c_float), ('crv', VoltVarCrv), ('olrt', c_float),
        ('AutoVref', c_int * 2)
    ]

class WVCfg(Structure):
    _fields_ = [('ena', c_int), ('crv', WattVarCrv)]

class TripsCfg(Structure):
    _fields_ = [('vt', VoltTrips), ('ft', FreqTrips)]

class UL1741SbCfg(Structure):
    _fields_ = [
        ('es', ESCfg),
        ('trips', TripsCfg),
        ('fw', FWCfg), ('vw', VWCfg), ('lap', LAPCfg),
        ('cpf', CPFCfg), ('crp', CRPCfg), ('vv', VVCfg), ('wv', WVCfg)
    ]

class UL1741SbInput(Structure):
    _fields_ = [('v', c_float), ('f', c_float), ('ap', c_float)]

class UL1741SbCmd(Structure):
    _fields_ = [('p', c_float), ('q', c_float), ('poc', c_int)]

# Access global config variable
ul1741sb_cfg = UL1741SbCfg.in_dll(derc, 'ul1741sb_cfg')

class DercEut(Eut):
    def __init__(self, **kwargs):
        # Initialize DLL
        derc.ul1741sb_step.argtypes = [POINTER(UL1741SbInput), c_float, c_bool, POINTER(UL1741SbCmd)]
        derc.ul1741sb_step.restype = c_int
        derc.ul1741sb_init_defaults.argtypes = []
        derc.ul1741sb_init_defaults.restype = c_int
        derc.ul1741sb_init_defaults()

        ul1741sb_cfg.es.ena = 1  # ENABLED
        ul1741sb_cfg.es.ov = 1.20    # 120% over-voltage
        ul1741sb_cfg.es.uv = 0.70    # 70% under-voltage
        ul1741sb_cfg.es.of = 62.0    # 62 Hz over-frequency
        ul1741sb_cfg.es.uf = 58.0    # 58 Hz under-frequency
        ul1741sb_cfg.es.delay = 0.0  # Instant enter service (no delay)
        ul1741sb_cfg.es.ramp_time = 0.0  # Instant ramp-up

        # EUT configuration
        self.Prated = 5000
        self.Srated = 5000
        self.VN = 240
        olrt = super().Olrt(crp=10, cpf=10, wv=10, lap=1)
        super().__init__(
            olrt=olrt,
            Cat=Eut.Category.B,
            aopCat=Eut.AOPCat.III,
            voltshalltrip_tbl=VoltShallTripTable.AOPCatIII(240),
            freqshalltrip_tbl=FreqShallTripTable.MaxRange(),
            Prated=self.Prated,
            Prated_prime=-self.Prated,
            Srated=self.Srated,
            Vin_nom=400,
            Vin_min=None,
            Vin_max=None,
            VN=self.VN,
            VL=self.VN * 0.9,
            VH=self.VN * 1.1,
            Pmin=0,
            Pmin_prime=0,
            Qrated_abs=5000,
            Qrated_inj=5000,
            Comms=[Eut.Comms.SUNS],
            multiphase=False,
            fL=59.0,
            fN=60.0,
            fH=61.0,
            vfo_capable=False,
            demonstrable_rocof=float('inf'),
            delta_Psmall=0.1,
        )

        self.current_cmd = UL1741SbCmd(p=0, q=0, poc=0)
        self.current_input = UL1741SbInput(v=1.0, f=60.0, ap=1.0)

    def dc_config(self, **kwargs):
        pass

    def set_cpf(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                ul1741sb_cfg.cpf.ena = 1 if v else 0
            elif k == 'PF':
                ul1741sb_cfg.cpf.pf = v
            elif k == 'Exct':
                ul1741sb_cfg.cpf.exct = 1 if v.upper() == 'INJ' else 0
            else:
                raise NotImplementedError

    def set_lap(self, Ena: bool, pu):
        ul1741sb_cfg.lap.ena = 1 if Ena else 0
        ul1741sb_cfg.lap.ap = pu

    def set_ap(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'pu':
                self.current_input.ap = v
            elif k == 'Ena':
                pass
            else:
                raise NotImplementedError

    def set_crp(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                ul1741sb_cfg.crp.ena = 1 if v else 0
            elif k == 'pu':
                ul1741sb_cfg.crp.var = v
            else:
                raise NotImplementedError

    def set_vv(self, Ena: bool, crv=None, vrefEna=None, vrefTr_s=None):
        ul1741sb_cfg.vv.ena = 1 if Ena else 0
        if crv is not None:
            ul1741sb_cfg.vv.crv.pts[0].x = crv.V1
            ul1741sb_cfg.vv.crv.pts[0].y = crv.Q1
            ul1741sb_cfg.vv.crv.pts[1].x = crv.V2
            ul1741sb_cfg.vv.crv.pts[1].y = crv.Q2
            ul1741sb_cfg.vv.crv.pts[2].x = crv.V3
            ul1741sb_cfg.vv.crv.pts[2].y = crv.Q3
            ul1741sb_cfg.vv.crv.pts[3].x = crv.V4
            ul1741sb_cfg.vv.crv.pts[3].y = crv.Q4
            ul1741sb_cfg.vv.olrt = crv.Tr
        if vrefEna is not None:
            ul1741sb_cfg.vv.AutoVref[0] = 1 if vrefEna else 0
        if vrefTr_s is not None:
            ul1741sb_cfg.vv.AutoVref[1] = vrefTr_s

    def set_wv(self, Ena: bool, crv=None):
        ul1741sb_cfg.wv.ena = 1 if Ena else 0
        if crv is not None:
            ul1741sb_cfg.wv.crv.pts[0].x = crv.P1
            ul1741sb_cfg.wv.crv.pts[0].y = crv.Q1
            ul1741sb_cfg.wv.crv.pts[1].x = crv.P2
            ul1741sb_cfg.wv.crv.pts[1].y = crv.Q2
            ul1741sb_cfg.wv.crv.pts[2].x = crv.P3
            ul1741sb_cfg.wv.crv.pts[2].y = crv.Q3
            ul1741sb_cfg.wv.crv.pts[3].x = crv.P1_prime
            ul1741sb_cfg.wv.crv.pts[3].y = crv.Q1_prime
            ul1741sb_cfg.wv.crv.pts[4].x = crv.P2_prime
            ul1741sb_cfg.wv.crv.pts[4].y = crv.Q2_prime
            ul1741sb_cfg.wv.crv.pts[5].x = crv.P3_prime
            ul1741sb_cfg.wv.crv.pts[5].y = crv.Q3_prime

    def set_vw(self, Ena: bool, crv=None):
        ul1741sb_cfg.vw.ena = 1 if Ena else 0
        if crv is not None:
            ul1741sb_cfg.vw.crv.pts[0].x = crv.V1
            ul1741sb_cfg.vw.crv.pts[0].y = crv.P1
            ul1741sb_cfg.vw.crv.pts[1].x = crv.V2
            ul1741sb_cfg.vw.crv.pts[1].y = crv.P2
            ul1741sb_cfg.vw.olrt = crv.Tr

    def set_vt(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'OV2':
                ul1741sb_cfg.trips.vt.ov2.mag = v['vpu']
                ul1741sb_cfg.trips.vt.ov2.cts = v['cts']
            elif k == 'OV1':
                ul1741sb_cfg.trips.vt.ov1.mag = v['vpu']
                ul1741sb_cfg.trips.vt.ov1.cts = v['cts']
            elif k == 'UV1':
                ul1741sb_cfg.trips.vt.uv1.mag = v['vpu']
                ul1741sb_cfg.trips.vt.uv1.cts = v['cts']
            elif k == 'UV2':
                ul1741sb_cfg.trips.vt.uv2.mag = v['vpu']
                ul1741sb_cfg.trips.vt.uv2.cts = v['cts']
            else:
                raise NotImplementedError

    def set_ft(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'OF2':
                ul1741sb_cfg.trips.ft.of2.mag = v['freq']
                ul1741sb_cfg.trips.ft.of2.cts = v['cts']
            elif k == 'OF1':
                ul1741sb_cfg.trips.ft.of1.mag = v['freq']
                ul1741sb_cfg.trips.ft.of1.cts = v['cts']
            elif k == 'UF1':
                ul1741sb_cfg.trips.ft.uf1.mag = v['freq']
                ul1741sb_cfg.trips.ft.uf1.cts = v['cts']
            elif k == 'UF2':
                ul1741sb_cfg.trips.ft.uf2.mag = v['freq']
                ul1741sb_cfg.trips.ft.uf2.cts = v['cts']
            else:
                raise NotImplementedError

    def has_tripped(self):
        return self.current_cmd.poc == 2  # TRIPPED

    def set_fw(self, Ena: bool, crv=None):
        ul1741sb_cfg.fw.ena = 1 if Ena else 0
        if crv is not None:
            ul1741sb_cfg.fw.of[0] = crv.dbof_hz  # db
            ul1741sb_cfg.fw.of[1] = crv.kof      # k
            ul1741sb_cfg.fw.uf[0] = crv.dbuf_hz
            ul1741sb_cfg.fw.uf[1] = crv.kuf
            ul1741sb_cfg.fw.olrt = crv.tr

    def set_es(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                ul1741sb_cfg.es.ena = 1 if v else 0
            elif k == 'esDelay':
                ul1741sb_cfg.es.delay = v
            elif k == 'esPeriod':
                ul1741sb_cfg.es.ramp_time = v
            elif k == 'esVpuHi':
                ul1741sb_cfg.es.ov = v
            elif k == 'esVpuLo':
                ul1741sb_cfg.es.uv = v
            elif k == 'esfHzHi':
                ul1741sb_cfg.es.of = v
            elif k == 'esfHzLo':
                ul1741sb_cfg.es.uf = v
            else:
                raise NotImplementedError

    def run_step(self, v_pu=None, f_hz=None, ap_pu=None, dt=0.1, fault=False):
        if v_pu is not None:
            self.current_input.v = v_pu
        if f_hz is not None:
            self.current_input.f = f_hz
        if ap_pu is not None:
            self.current_input.ap = ap_pu

        derc.ul1741sb_step(byref(self.current_input), dt, fault, byref(self.current_cmd))

    @property
    def p_out_w(self):
        return self.current_cmd.p * self.Prated

    @property
    def q_out_var(self):
        return self.current_cmd.q * self.Srated

    @property
    def der_status(self):
        states = {0: 'Normal', 1: 'Ceased', 2: 'Trip'}
        return states.get(self.current_cmd.poc, 'Unknown')