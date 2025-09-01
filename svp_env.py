from datetime import timedelta, datetime
from http.client import UnimplementedFileMode


class Env:  # step voltage, power, sleep, etc.
    def __init__(self, ts, grid, daq):
        self.ts = ts
        self.grid = grid
        self.daq = daq

    def elapsed_since(self, interval: timedelta, start: datetime) -> bool:
        return datetime.now() - start >= interval

    def time_now(self):
        datetime.now()

    def sleep(self, td: timedelta):
        self.ts.sleep(td.seconds)

    def meas(self, *args):
        self.daq.data_sample()
        data = self.daq.data_capture_read()
        return (data[arg] for arg in args)

    def ac_config(self, **kwargs):
        if 'Vac' in kwargs.keys():
            self.grid.voltage(kwargs['Vac'])

    def ac_config_asym(self, **kwargs):
        raise NotImplementedError

    def eut_power(self, **kwargs):
        pass

    def log(self, **kwargs):
        self.ts.log(kwargs['msg'])
