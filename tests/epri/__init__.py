from pyUL1741SB.UL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd

std = UL1741SB()
eut = EpriEut()
env = EpriEnv(eut)

# std.cpf_proc(env=env, eut=eut)
# std.crp_proc(env=env, eut=eut)
# std.vv_proc(env=env, eut=eut)

# std.vv_vref_proc(env=env, eut=eut)
# print(env.vv_vref_results)

# std.wv_proc(env=env, eut=eut)
# print(env.wv_results)

# std.ovt_proc(env=env, eut=eut)
# std.uvt_proc(env=env, eut=eut)
# print(env.ovt_results)
# print(env.uvt_results)
# std.oft_proc(env=env, eut=eut)
# std.uft_proc(env=env, eut=eut)
# print(env.oft_results)
# print(env.uft_results)

# df = pd.concat(env.cpf_results.loc[:, 'data'].values)
# df = pd.concat(env.crp_results.loc[:, 'data'].values)

# std.vw_proc(env=env, eut=eut)
# df = pd.concat(env.vw_results.loc[:, 'data'].values)

std.fwo_proc(env=env, eut=eut)
df = pd.concat(env.fwo_results.loc[:, 'data'].values)
pass
