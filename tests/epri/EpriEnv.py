import pandas as pd
import datetime as dt
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable
from EpriEut import EpriEut
import opender as der

class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0)
        self.eut = eut
        self.cpf_results = pd.DataFrame()
        self.cpf_results = pd.DataFrame()
        self.crp_results = pd.DataFrame()
        self.vv_results = pd.DataFrame()
        self.ov_results = pd.DataFrame()
        self.uv_results = pd.DataFrame()

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

    def log(self, **kwargs):
        print(kwargs['msg'])

    def validate(self, dct_label: dict):
        df_row = pd.DataFrame([dct_label])
        proc = dct_label.pop('proc')
        if proc == 'cpf':
            self.cpf_results = pd.concat([self.cpf_results, df_row])
        elif proc == 'crp':
            self.crp_results = pd.concat([self.crp_results, df_row])
        elif proc == 'vv':
            self.vv_results = pd.concat([self.vv_results, df_row])
        elif proc == 'uvt':
            self.uv_results = pd.concat([self.uv_results, df_row])
        elif proc == 'ovt':
            self.ov_results = pd.concat([self.ov_results, df_row])
        else:
            raise NotImplementedError

    def pre_cbk(self, **kwargs):
        print(f"pre: {''.join([f'{k}: {v}; ' for k, v in kwargs.items()])}")

    def post_cbk(self, **kwargs):
        print(f"post: {''.join([f'{k}: {v}; ' for k, v in kwargs.items()])}")

    def ac_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.der.update_der_input(v_pu=v/self.eut.der.der_file.NP_AC_V_NOM)
            else:
                raise NotImplementedError

    def dc_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'power':
                self.eut.der.update_der_input(p_dc_w=v)
            elif k =='Vdc':
                pass
            else:
                raise NotImplementedError
