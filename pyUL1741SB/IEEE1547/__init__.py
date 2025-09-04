from pyUL1741SB.IEEE1547.VoltReg import VoltReg

class IEEE1547(VoltReg):
    pass

    def ss_eval_4p2(self, env, label, y_of_x, x_ss, y_ss, xMRA, yMRA):
        y_min = min(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) - 1.5 * yMRA
        y_max = max(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) + 1.5 * yMRA
        # y_targ = y_of_x(x_ss)
        if y_min <= y_ss <= y_max:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"{label} steady state {passfail} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])")
