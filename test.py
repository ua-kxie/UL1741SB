from pyUL1741SB.UL1741SB import UL1741SB
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable

std = UL1741SB()
eut = Eut(
    Cat=Eut.Category.A,
    aopCat=Eut.AOPCat.III,
    voltshalltrip_tbl=VoltShallTripTable.AOPCatIII(240),
    freqshalltrip_tbl=FreqShallTripTable.MaxRange(),
    vfo=True,
    rocof=3,
    Prated=5e3,
    Prated_prime=800,
    Srated=1200,
    Vin_nom=56,
    Vin_min=None,
    Vin_max=None,
    VN=240,
    VL=220,
    VH=260,
    Pmin=100,
    Pmin_prime=80,
    Qrated_abs=500,
    Qrated_inj=-500,
    Comms=[Eut.Comms.SUNS],
    multiphase=False,
    fL=59.0,  # minimum frequency in continuous operating region (Hz)
    fN=60.0,  # nominal frequency (Hz)
    fH=61.0,  # maximum frequency in continuous operating region (Hz)
    delta_Psmall=0.1,  # small power change threshold (p.u.)
    delta_Plarge=0.5   # large power change threshold (p.u.)
)
env = Env()
std.cpf_proc(env=env, eut=eut)
std.vv_proc(env=env, eut=eut)
std.crp_proc(env=env, eut=eut)
std.of_trip_proc(env=env, eut=eut)
std.uf_trip_proc(env=env, eut=eut)
std.hfrt_proc(env=env, eut=eut)
std.lfrt_proc(env=env, eut=eut)
std.hfrt_proc(env=env, eut=eut)
std.ov_trip_proc(env=env, eut=eut)
std.uv_trip_proc(env=env, eut=eut)
std.ovrt_proc(env=env, eut=eut)
std.uvrt_proc(env=env, eut=eut)
