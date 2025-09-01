from datetime import timedelta

class Env:  # step voltage, power, sleep, etc.
    def __init__(self):
        pass

    def sleep(self, td: timedelta):
        pass

    def meas(self, *args):
        return (1,) * len(args)

    def ac_config(self, **kwargs):
        pass

    def ac_config_asym(self, **kwargs):
        pass

    def eut_power(self, **kwargs):
        pass

    def log_result(self, **kwargs):
        pass