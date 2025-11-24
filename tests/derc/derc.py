from ctypes import *
import os

# Load DLL from current directory
derc = CDLL(rf'C:\Users\Iraeis\PycharmProjects\DerC\test\dll\build\derc.dll')


# Define structures matching derc.h
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


class DerCCfg(Structure):
    _fields_ = [
        ('es', ESCfg),
        ('trips', TripsCfg),
        ('fw', FWCfg), ('vw', VWCfg), ('lap', LAPCfg),
        ('cpf', CPFCfg), ('crp', CRPCfg), ('vv', VVCfg), ('wv', WVCfg)
    ]


class DerCInput(Structure):
    _fields_ = [('v', c_float), ('f', c_float), ('ap', c_float)]


class DerCCmd(Structure):
    _fields_ = [('p', c_float), ('q', c_float), ('poc', c_int)]


# Access global config variable
derc_cfg = DerCCfg.in_dll(derc, 'derc_cfg')

# Configure function prototypes
derc.derc_step.argtypes = [POINTER(DerCInput), c_float, c_bool, POINTER(DerCCmd)]
derc.derc_step.restype = c_int

# Configuration functions
def enable_volt_var(vref=1.0, olrt=5.0, curve_points=None):
    derc_cfg.vv.ena = 1  # ENABLED
    derc_cfg.vv.vref = vref
    derc_cfg.vv.olrt = olrt
    if curve_points:
        for i, (v, q) in enumerate(curve_points):
            derc_cfg.vv.crv.pts[i].x = v
            derc_cfg.vv.crv.pts[i].y = q


def enable_freq_watt(db_of=60.5, db_uf=59.5, k_of=0.05, k_uf=0.05, olrt=5.0):
    derc_cfg.fw.ena = 1
    derc_cfg.fw.of[0] = db_of  # db
    derc_cfg.fw.of[1] = k_of  # k
    derc_cfg.fw.uf[0] = db_uf
    derc_cfg.fw.uf[1] = k_uf
    derc_cfg.fw.olrt = olrt


def enable_volt_watt(v1=1.06, p1=1.0, v2=1.10, p2=0.0, olrt=5.0):
    derc_cfg.vw.ena = 1
    derc_cfg.vw.crv.pts[0].x = v1
    derc_cfg.vw.crv.pts[0].y = p1
    derc_cfg.vw.crv.pts[1].x = v2
    derc_cfg.vw.crv.pts[1].y = p2
    derc_cfg.vw.olrt = olrt


def set_power_limit(limit_pu=1.0):
    derc_cfg.lap.ena = 1
    derc_cfg.lap.ap = limit_pu


def set_constant_pf(pf=1.0, excitation=1):  # 1=OVER_EXCITED, 0=UNDER_EXCITED
    derc_cfg.cpf.ena = 1
    derc_cfg.cpf.pf = pf
    derc_cfg.cpf.exct = excitation


def set_constant_reactive_power(var_pu=0.0):
    derc_cfg.crp.ena = 1
    derc_cfg.crp.var = var_pu


def set_voltage_trips(ov1_v=1.10, ov1_t=0.16, ov2_v=1.20, ov2_t=0.16,
                      uv1_v=0.88, uv1_t=2.00, uv2_v=0.50, uv2_t=0.16):
    derc_cfg.trips.vt.ov1.mag = ov1_v
    derc_cfg.trips.vt.ov1.cts = ov1_t
    derc_cfg.trips.vt.ov2.mag = ov2_v
    derc_cfg.trips.vt.ov2.cts = ov2_t
    derc_cfg.trips.vt.uv1.mag = uv1_v
    derc_cfg.trips.vt.uv1.cts = uv1_t
    derc_cfg.trips.vt.uv2.mag = uv2_v
    derc_cfg.trips.vt.uv2.cts = uv2_t


# Test function
def run_step(v_pu=1.0, f_hz=60.0, ap_pu=1.0, dt=0.01, fault=False):
    inp = DerCInput(v=v_pu, f=f_hz, ap=ap_pu)
    cmd = DerCCmd()
    derc.derc_step(byref(inp), dt, fault, byref(cmd))
    states = {0: 'CONN', 1: 'CEASED', 2: 'TRIPPED'}
    return cmd.p, cmd.q, states.get(cmd.poc, 'UNKNOWN')


# Example usage
if __name__ == "__main__":
    # Configure curves
    derc_cfg.es.ena = 1  # ENABLED
    derc_cfg.es.ov = 1.20  # 120% over-voltage
    derc_cfg.es.uv = 0.70  # 70% under-voltage
    derc_cfg.es.of = 62.0  # 62 Hz over-frequency
    derc_cfg.es.uf = 58.0  # 58 Hz under-frequency
    derc_cfg.es.delay = 0.0  # Instant enter service (no delay)
    derc_cfg.es.ramp_time = 0.0  # Instant ramp-up

    enable_volt_var(vref=1.0, olrt=1.0, curve_points=[
        (0.92, 0.44), (0.98, 0.0), (1.02, 0.0), (1.08, -0.44)
    ])

    # Test
    p, q, state = run_step(v_pu=1.05, f_hz=59.8)
    print(f"P: {p:.3f} pu, Q: {q:.3f} pu, State: {state}")