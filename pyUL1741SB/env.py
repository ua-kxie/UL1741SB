from datetime import timedelta, datetime

class Env:  # step voltage, power, sleep, etc.
    def __init__(self):
        pass

    def elapsed_since(self, interval: timedelta, start: datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        for i in range(10-1, -1, -1):
            yield i == 0

    def time_now(self):
        return datetime.now()

    def sleep(self, td: timedelta):
        pass

    def meas(self, *args):
        return (1,) * len(args)

    def ac_config(self, **kwargs):
        pass

    def ac_config_asym(self, **kwargs):
        pass

    def log(self, **kwargs):
        print(kwargs['msg'])

    def dc_config(self, **kwargs):
        pass
