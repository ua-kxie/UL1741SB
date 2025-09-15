import opender as der
import pandas as pd
import datetime as dt
from pyUL1741SB.UL1741SB import UL1741SB
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve

std = UL1741SB()

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
            rocof=3,
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
    # eut.fixed_pf(Ena=True, PF=targetPF)
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
    def active_power(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                self.der.der_file.AP_LIMIT_ENABLE = v
            elif k == 'pu':
                self.der.der_file.AP_LIMIT = v
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
    def vv(self, Ena, crv:VVCurve=None):
        self.der.der_file.QV_MODE_ENABLE = Ena
        if crv is not None:
            self.der.der_file.QV_CURVE_Q1 = crv.Q1 / self.der.der_file.NP_VA_MAX
            self.der.der_file.QV_CURVE_Q2 = crv.Q2 / self.der.der_file.NP_VA_MAX
            self.der.der_file.QV_CURVE_Q3 = crv.Q3 / self.der.der_file.NP_VA_MAX
            self.der.der_file.QV_CURVE_Q4 = crv.Q4 / self.der.der_file.NP_VA_MAX
            self.der.der_file.QV_CURVE_V1 = crv.V1 / self.der.der_file.NP_AC_V_NOM
            self.der.der_file.QV_CURVE_V2 = crv.V2 / self.der.der_file.NP_AC_V_NOM
            self.der.der_file.QV_CURVE_V3 = crv.V3 / self.der.der_file.NP_AC_V_NOM
            self.der.der_file.QV_CURVE_V4 = crv.V4 / self.der.der_file.NP_AC_V_NOM
            self.der.der_file.QV_OLRT = crv.Tr

eut = EpriEut()


class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0)
        self.eut = eut
        self.cpf_results = pd.DataFrame()
        self.crp_results = pd.DataFrame()
        self.vv_results = pd.DataFrame()

    def elapsed_since(self, interval: dt.timedelta, start: dt.datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: dt.timedelta):
        self.time += td
        der.DER.t_s = td.total_seconds()
        self.eut.der.run()

    def meas(self):
        data = {
            'time': self.time,
            'P': self.eut.der.der_output.p_out_w,
            'Q': self.eut.der.der_output.q_out_var,
            'V': self.eut.der.der_input.v_meas_pu * self.eut.der.der_file.NP_AC_V_NOM
        }
        return data

    def meas_single(self, *args) -> pd.DataFrame:
        dct = self.meas()
        df = pd.DataFrame([dct]).set_index('time').loc[:, [*args]]
        self.time += dt.timedelta(seconds=0.01)
        return df

    def meas_for(self, dur: dt.timedelta, tres: dt.timedelta, *args) -> pd.DataFrame:
        start = self.time
        dfs = []
        der.DER.t_s = tres.total_seconds()

        while self.time - start < dur:
            dfs.append(self.meas())
            self.eut.der.run()
            self.time += tres
        df = pd.DataFrame(dfs).set_index('time').loc[:, [*args]]
        return df

    def ac_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.der.update_der_input(v_pu=v/self.eut.der.der_file.NP_AC_V_NOM)
            else:
                raise NotImplementedError

    def ac_config_asym(self, **kwargs):
        raise NotImplementedError

    def log(self, **kwargs):
        print(kwargs['msg'])

    def dc_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'power':
                self.eut.der.update_der_input(p_dc_w=v)
            elif k =='Vin':
                pass
            else:
                raise NotImplementedError

    def validate(self, dct_label: dict):
        df_row = pd.DataFrame([dct_label])
        proc = dct_label.pop('proc')
        if proc == 'cpf':
            self.cpf_results = pd.concat([self.cpf_results, df_row])
        elif proc == 'crp':
            self.crp_results = pd.concat([self.crp_results, df_row])
        elif proc == 'vv':
            self.vv_results = pd.concat([self.vv_results, df_row])
env = EpriEnv(eut)

# std.cpf_proc(env=env, eut=eut)
# std.crp_proc(env=env, eut=eut)
std.vv_proc(env=env, eut=eut)

print(env.crp_results)
