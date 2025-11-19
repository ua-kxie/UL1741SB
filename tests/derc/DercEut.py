from ctypes import *
from pyUL1741SB import Eut
from pyUL1741SB.eut import VoltShallTripTable, FreqShallTripTable

# Load DLL
derc = CDLL(rf'C:\Users\Iraeis\PycharmProjects\Supervisory1741SB\derc\build\derc.dll')

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

class FreqWattCfg(Structure):
    _fields_ = [('db', c_float), ('k', c_float)]

class FWCfg(Structure):
    _fields_ = [
        ('of', FreqWattCfg),
        ('uf', FreqWattCfg),
        ('ena', c_int),
        ('olrt', c_float)
    ]

class VWCfg(Structure):
    _fields_ = [('ena', c_int), ('crv', VoltWattCrv), ('olrt', c_float)]

class LAPCfg(Structure):
    _fields_ = [('ena', c_int), ('ap', c_float)]

class CPFCfg(Structure):
    _fields_ = [('ena', c_int), ('pf', c_float), ('exct', c_int)]

class CRPCfg(Structure):
    _fields_ = [('ena', c_int), ('var', c_float)]

class AutoVrefCfg(Structure):
    _fields_ = [("ena", c_int), ("olrt", c_float)]

class VVCfg(Structure):
    _fields_ = [
        ('ena', c_int), ('vref', c_float), ('crv', VoltVarCrv), ('olrt', c_float),
        ('AutoVref', AutoVrefCfg)
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

class DercEut(Eut):
    def __init__(self, **kwargs):
        # Initialize DLL
        derc.ul1741sb_step.argtypes = [POINTER(UL1741SbInput), c_float, c_bool, POINTER(UL1741SbCmd)]
        derc.ul1741sb_step.restype = c_int
        
        self.cfg = UL1741SbCfg.in_dll(derc, 'ul1741sb_cfg')

        self.cfg.es.ena = 1  # ENABLED
        self.cfg.es.ov = 1.20  # 120% over-voltage
        self.cfg.es.uv = 0.70  # 70% under-voltage
        self.cfg.es.of = 62.0  # 62 Hz over-frequency
        self.cfg.es.uf = 58.0  # 58 Hz under-frequency
        self.cfg.es.delay = 0.016  # 0.16 seconds delay
        self.cfg.es.ramp_time = 0.016  # 5 minutes ramp time

        # Voltage trip defaults (Category I)
        self.cfg.trips.vt.ov1.mag = 1.10  # 110%
        self.cfg.trips.vt.ov1.cts = 0.16  # 0.16s
        self.cfg.trips.vt.ov2.mag = 1.20  # 120%
        self.cfg.trips.vt.ov2.cts = 0.16  # 0.16s
        self.cfg.trips.vt.uv1.mag = 0.88  # 88%
        self.cfg.trips.vt.uv1.cts = 2.00  # 2.0s
        self.cfg.trips.vt.uv2.mag = 0.50  # 50%
        self.cfg.trips.vt.uv2.cts = 0.16  # 0.16s

        # Frequency trip defaults (Category I)
        self.cfg.trips.ft.of1.mag = 61.2  # 61.2 Hz
        self.cfg.trips.ft.of1.cts = 300.0  # 5 minutes
        self.cfg.trips.ft.of2.mag = 62.0  # 62.0 Hz
        self.cfg.trips.ft.of2.cts = 0.16  # 0.16s
        self.cfg.trips.ft.uf1.mag = 58.8  # 58.8 Hz
        self.cfg.trips.ft.uf1.cts = 300.0  # 5 minutes
        self.cfg.trips.ft.uf2.mag = 57.0  # 57.0 Hz
        self.cfg.trips.ft.uf2.cts = 0.16  # 0.16s

        # Frequency-Watt defaults
        self.cfg.fw.ena = 1  # ENABLED
        self.cfg.fw.of.db = 0.036
        self.cfg.fw.of.k = 0.05  # 5% power reduction per Hz
        self.cfg.fw.uf.db = 0.036
        self.cfg.fw.uf.k = 0.05  # 5% power reduction per Hz
        self.cfg.fw.olrt = 5.0  # 5 seconds response time

        # Volt-Watt defaults
        self.cfg.vw.ena = 0  # DISABLED
        self.cfg.vw.crv.pts[0].x = 1.06  # 106% voltage
        self.cfg.vw.crv.pts[0].y = 1.00  # 100% power
        self.cfg.vw.crv.pts[1].x = 1.10  # 110% voltage
        self.cfg.vw.crv.pts[1].y = 0.00  # 0% power
        self.cfg.vw.olrt = 5.0  # 5 seconds response time

        # Limit Active Power defaults
        self.cfg.lap.ena = 0  # DISABLED
        self.cfg.lap.ap = 1.00  # 100% power limit

        # Constant Power Factor defaults
        self.cfg.cpf.ena = 1  # ENABLED
        self.cfg.cpf.pf = 1.00  # Unity power factor
        self.cfg.cpf.exct = 1  # OVER_EXCITED (assuming 1 = OVER_EXCITED)

        # Constant Reactive Power defaults
        self.cfg.crp.ena = 0  # DISABLED
        self.cfg.crp.var = 0.00  # Zero reactive power

        # Volt-Var defaults
        self.cfg.vv.ena = 0  # DISABLED
        self.cfg.vv.vref = 1.00  # 100% reference voltage
        self.cfg.vv.crv.pts[0].x = 0.92  # 92% voltage
        self.cfg.vv.crv.pts[0].y = 0.44  # 44% reactive power (injection)
        self.cfg.vv.crv.pts[1].x = 0.98  # 98% voltage
        self.cfg.vv.crv.pts[1].y = 0.00  # 0% reactive power
        self.cfg.vv.crv.pts[2].x = 1.02  # 102% voltage
        self.cfg.vv.crv.pts[2].y = 0.00  # 0% reactive power
        self.cfg.vv.crv.pts[3].x = 1.08  # 108% voltage
        self.cfg.vv.crv.pts[3].y = -0.44  # 44% reactive power (absorption)
        self.cfg.vv.olrt = 5.0  # 5 seconds response time
        self.cfg.vv.AutoVref.ena = 0  # DISABLED
        self.cfg.vv.AutoVref.olrt = 300.0  # 5 minutes response time

        # Watt-Var defaults
        self.cfg.wv.ena = 0  # DISABLED
        self.cfg.wv.crv.pts[0].x = -1.0  # 0% power
        self.cfg.wv.crv.pts[0].y = 0.44  # 44% reactive power
        self.cfg.wv.crv.pts[1].x = -0.5  # 20% power
        self.cfg.wv.crv.pts[1].y = 0.00  # 44% reactive power
        self.cfg.wv.crv.pts[2].x = 0.00  # 30% power
        self.cfg.wv.crv.pts[2].y = 0.00  # 0% reactive power
        self.cfg.wv.crv.pts[3].x = 0.00  # 70% power
        self.cfg.wv.crv.pts[3].y = 0.00  # 0% reactive power
        self.cfg.wv.crv.pts[4].x = 0.50  # 80% power
        self.cfg.wv.crv.pts[4].y = 0.00  # 44% reactive power (absorption)
        self.cfg.wv.crv.pts[5].x = 1.00  # 100% power
        self.cfg.wv.crv.pts[5].y = -0.44  # 44% reactive power (absorption)

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
                self.cfg.cpf.ena = 1 if v else 0
            elif k == 'PF':
                self.cfg.cpf.pf = v
            elif k == 'Exct':
                self.cfg.cpf.exct = 1 if v.upper() == 'INJ' else 0
            else:
                raise NotImplementedError

    def set_lap(self, Ena: bool, pu):
        self.cfg.lap.ena = 1 if Ena else 0
        self.cfg.lap.ap = pu

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
                self.cfg.crp.ena = 1 if v else 0
            elif k == 'pu':
                self.cfg.crp.var = v
            else:
                raise NotImplementedError

    def set_vv(self, Ena: bool, crv=None, vrefEna=None, vrefTr_s=None):
        self.cfg.vv.ena = 1 if Ena else 0
        if crv is not None:
            self.cfg.vv.crv.pts[0].x = crv.V1
            self.cfg.vv.crv.pts[0].y = crv.Q1
            self.cfg.vv.crv.pts[1].x = crv.V2
            self.cfg.vv.crv.pts[1].y = crv.Q2
            self.cfg.vv.crv.pts[2].x = crv.V3
            self.cfg.vv.crv.pts[2].y = crv.Q3
            self.cfg.vv.crv.pts[3].x = crv.V4
            self.cfg.vv.crv.pts[3].y = crv.Q4
            self.cfg.vv.olrt = crv.Tr
        if vrefEna is not None:
            self.cfg.vv.AutoVref.ena = 1 if vrefEna else 0
        if vrefTr_s is not None:
            self.cfg.vv.AutoVref.olrt = vrefTr_s

    def set_wv(self, Ena: bool, crv=None):
        self.cfg.wv.ena = 1 if Ena else 0
        if crv is not None:
            self.cfg.wv.crv.pts[0].x = crv.P3_prime
            self.cfg.wv.crv.pts[0].y = crv.Q3_prime
            self.cfg.wv.crv.pts[1].x = crv.P2_prime
            self.cfg.wv.crv.pts[1].y = crv.Q2_prime
            self.cfg.wv.crv.pts[2].x = crv.P1_prime
            self.cfg.wv.crv.pts[2].y = crv.Q1_prime
            self.cfg.wv.crv.pts[3].x = crv.P1
            self.cfg.wv.crv.pts[3].y = crv.Q1
            self.cfg.wv.crv.pts[4].x = crv.P2
            self.cfg.wv.crv.pts[4].y = crv.Q2
            self.cfg.wv.crv.pts[5].x = crv.P3
            self.cfg.wv.crv.pts[5].y = crv.Q3

    def set_vw(self, Ena: bool, crv=None):
        self.cfg.vw.ena = 1 if Ena else 0
        if crv is not None:
            self.cfg.vw.crv.pts[0].x = crv.V1
            self.cfg.vw.crv.pts[0].y = crv.P1
            self.cfg.vw.crv.pts[1].x = crv.V2
            self.cfg.vw.crv.pts[1].y = crv.P2
            self.cfg.vw.olrt = crv.Tr

    def set_vt(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'OV2':
                self.cfg.trips.vt.ov2.mag = v['vpu']
                self.cfg.trips.vt.ov2.cts = v['cts']
            elif k == 'OV1':
                self.cfg.trips.vt.ov1.mag = v['vpu']
                self.cfg.trips.vt.ov1.cts = v['cts']
            elif k == 'UV1':
                self.cfg.trips.vt.uv1.mag = v['vpu']
                self.cfg.trips.vt.uv1.cts = v['cts']
            elif k == 'UV2':
                self.cfg.trips.vt.uv2.mag = v['vpu']
                self.cfg.trips.vt.uv2.cts = v['cts']
            else:
                raise NotImplementedError

    def set_ft(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'OF2':
                self.cfg.trips.ft.of2.mag = v['freq']
                self.cfg.trips.ft.of2.cts = v['cts']
            elif k == 'OF1':
                self.cfg.trips.ft.of1.mag = v['freq']
                self.cfg.trips.ft.of1.cts = v['cts']
            elif k == 'UF1':
                self.cfg.trips.ft.uf1.mag = v['freq']
                self.cfg.trips.ft.uf1.cts = v['cts']
            elif k == 'UF2':
                self.cfg.trips.ft.uf2.mag = v['freq']
                self.cfg.trips.ft.uf2.cts = v['cts']
            else:
                raise NotImplementedError

    def has_tripped(self):
        return self.current_cmd.poc == 2  # TRIPPED

    def set_fw(self, Ena: bool, crv=None):
        self.cfg.fw.ena = 1 if Ena else 0
        if crv is not None:
            self.cfg.fw.of.db = crv.dbof_hz  # db
            self.cfg.fw.of.k = crv.kof      # k
            self.cfg.fw.uf.db = crv.dbuf_hz
            self.cfg.fw.uf.k = crv.kuf
            self.cfg.fw.olrt = crv.tr

    def set_es(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                self.cfg.es.ena = 1 if v else 0
            elif k == 'esDelay':
                self.cfg.es.delay = v
            elif k == 'esPeriod':
                self.cfg.es.ramp_time = v
            elif k == 'esVpuHi':
                self.cfg.es.ov = v
            elif k == 'esVpuLo':
                self.cfg.es.uv = v
            elif k == 'esfHzHi':
                self.cfg.es.of = v
            elif k == 'esfHzLo':
                self.cfg.es.uf = v
            else:
                raise NotImplementedError

    def run_step(self, dt=0.1, fault=False):
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