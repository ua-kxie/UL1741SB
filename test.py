from pyUL1741SB.UL1741SB import UL1741SB
from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env

std = UL1741SB()
eut = Eut(
    Cat=Eut.Category.A,
    Prated=1000,
    Prated_prime=800,
    Srated=1200,
    Vin_nom=230,
    Vin_min=210,
    Vin_max=250,
    VN=120,
    VL=110,
    VH=130,
    Pmin=100,
    Pmin_prime=80,
    Qrated_abs=500,
    Qrated_inj=-500,
    Comms=[Eut.Comms.SUNS],
    multiphase=False
)
env = Env()
std.cpf_proc(env=env, eut=eut, Vins=[48], targetPFs=[0.9])
std.vv_proc(env=env, eut=eut)
