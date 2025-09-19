from pyUL1741SB.UL1741SB import UL1741SB

from EpriEnv import EpriEnv
from EpriEut import EpriEut

std = UL1741SB()
eut = EpriEut()
env = EpriEnv(eut)

std.ovt_proc(env=env, eut=eut)
std.uvt_proc(env=env, eut=eut)
print(env.uvt_results)
print(env.ovt_results)
# std.oft_proc(env=env, eut=eut)
# std.uft_proc(env=env, eut=eut)
# print(env.uft_results)
# print(env.oft_results)
# std.cpf_proc(env=env, eut=eut)
# std.crp_proc(env=env, eut=eut)
# std.vv_proc(env=env, eut=eut)

