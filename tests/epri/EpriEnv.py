import pandas as pd
import datetime as dt
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable
from EpriEut import EpriEut
import opender as der

DTS = 0.1

class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0)
        self.eut = eut
        self.cpf_results = pd.DataFrame()
        self.cpf_results = pd.DataFrame()
        self.crp_results = pd.DataFrame()
        self.vv_results = pd.DataFrame()
        self.ovt_results = pd.DataFrame()
        self.uvt_results = pd.DataFrame()
        self.oft_results = pd.DataFrame()
        self.uft_results = pd.DataFrame()
        self.vv_vref_results = pd.DataFrame()
        self.wv_results = pd.DataFrame()
        self.vw_results = pd.DataFrame()
        self.fwo_results = pd.DataFrame()

    def elapsed_since(self, interval: dt.timedelta, start: dt.datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: dt.timedelta):
        self.time += td
        der.DER.t_s = td.total_seconds()
        self.eut.der.run()
        der.DER.t_s = DTS

    def meas(self):
        data = {
            'time': self.time,
            'F': self.eut.der.der_input.freq_hz,
            'P': self.eut.der.der_output.p_out_w,
            'Q': self.eut.der.der_output.q_out_var,
            'V': self.eut.der.der_input.v_meas_pu * self.eut.der.der_file.NP_AC_V_NOM
        }
        return data

    def meas_single(self, *args) -> pd.DataFrame:
        dct = self.meas()
        der.DER.t_s = 0.01
        df = pd.DataFrame([dct]).set_index('time').loc[:, [*args]]
        self.time += dt.timedelta(seconds=0.01)
        der.DER.t_s = DTS
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
        der.DER.t_s = DTS
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
            self.uvt_results = pd.concat([self.uvt_results, df_row])
        elif proc == 'ovt':
            self.ovt_results = pd.concat([self.ovt_results, df_row])
        elif proc == 'uft':
            self.uft_results = pd.concat([self.uft_results, df_row])
        elif proc == 'oft':
            self.oft_results = pd.concat([self.oft_results, df_row])
        elif proc == 'vv-vref':
            self.vv_vref_results = pd.concat([self.vv_vref_results, df_row])
        elif proc == 'wv':
            self.wv_results = pd.concat([self.wv_results, df_row])
        elif proc == 'vw':
            self.vw_results = pd.concat([self.vw_results, df_row])
        elif proc == 'fwo':
            self.fwo_results = pd.concat([self.fwo_results, df_row])
        else:
            raise NotImplementedError(proc)

    def pre_cbk(self, **kwargs):
        pass

    def post_cbk(self, **kwargs):
        pass

    def ac_config(self, **kwargs):
        """"""
        '''
        block until settings are applied (i.e. wait for rocof-limited f change)
        '''
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.der.update_der_input(v_pu=v/self.eut.der.der_file.NP_AC_V_NOM)
            elif k =='freq':
                self.eut.der.update_der_input(f=v)
            elif k =='rocof':
                pass
            else:
                raise NotImplementedError(k)

    def dc_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'pwr_watts':
                self.eut.der.update_der_input(p_dem_pu=v)
            elif k =='Vdc':
                pass
            else:
                raise NotImplementedError(k)
