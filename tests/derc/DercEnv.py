import pandas as pd
import datetime as dt
from pyUL1741SB import Env
from DercEut import DercEut


class DercEnv(Env):
    def __init__(self, eut: DercEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
        self.eut = eut
        self.results = {}

    def elapsed_since(self, interval: dt.timedelta, start: dt.datetime) -> bool:
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: dt.timedelta):
        self.time += td
        self.eut.run_step(dt=td.total_seconds())

    def meas(self):
        v = self.eut.current_input.v * self.eut.VN
        data = {
            'time': self.time,
            'F': self.eut.current_input.f,
            'P': self.eut.p_out_w,
            'Q': self.eut.q_out_var,
            'V': v,
        }
        return data

    def meas_single(self, *args) -> pd.DataFrame:
        dct = self.meas()
        self.eut.run_step(dt=0.01)
        self.time += dt.timedelta(seconds=0.01)
        df = pd.DataFrame([dct]).set_index('time').loc[:, [*args]]
        return df

    def meas_for(self, dur: dt.timedelta, tres: dt.timedelta, *args) -> pd.DataFrame:
        start = self.time
        dfs = []
        while self.time - start < dur:
            dfs.append(self.meas())
            self.eut.run_step(dt=tres.total_seconds())
            self.time += tres
        df = pd.DataFrame(dfs).set_index('time').loc[:, [*args]]
        return df

    def log(self, **kwargs):
        print(kwargs['msg'])

    def ac_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.current_input.v = v/self.eut.VN
            elif k == 'freq':
                self.eut.current_input.f = v
            elif k == 'rocof':
                pass
            else:
                raise NotImplementedError(k)
