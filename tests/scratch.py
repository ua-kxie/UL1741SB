from opender import DER, DER_PV
import matplotlib.pyplot as plt

der_obj = DER_PV()
der_obj.der_file.CONST_PF_MODE_ENABLE=True
der_obj.der_file.CONST_PF=0.9
der_obj.update_der_input(v_pu=1, f=60, p_dc_pu = 1)
# Configure dynamic simulation timestep
t_s = 1
DER.t_s = t_s
t = 0

# Prepare arrays for plotting
t_plot = []
v_plot = []
p_plot = []
pdc_plot = []
q_plot = []

# Simulate for 45s
while t < 60:

    # voltage alternating between 1.05 and 1pu
    if 15 < t < 30:
        der_obj.update_der_input(v_pu=1)
    elif 45 < t < 60:
        der_obj.der_file.CONST_PF = 0.95
    else:
        der_obj.der_file.CONST_PF = 0.90
        der_obj.update_der_input(v_pu=1.05)

    # calculate output power each time step
    P, Q = der_obj.run()

    # save result
    t_plot.append(t)
    p_plot.append(der_obj.p_out_pu)
    pdc_plot.append(der_obj.der_input.p_avl_pu)
    q_plot.append(der_obj.q_out_pu)
    v_plot.append(der_obj.der_input.v_meas_pu)

    # increase t
    t = t + t_s



# plot figure
fig = plt.figure()
plt.clf()
ax1=plt.subplot(3, 1, 1)
plt.plot(t_plot, v_plot, label = 'Voltage (pu)')
plt.grid()
plt.legend()
plt.subplot(3, 1, 2, sharex=ax1)
plt.plot(t_plot, pdc_plot, label='P_dc (pu)')
plt.plot(t_plot, p_plot, label='P_out (pu)')
plt.grid()
plt.legend()
plt.subplot(3, 1, 3, sharex=ax1)
plt.plot(t_plot, q_plot, label='Q_out (pu)')
plt.grid()
plt.legend()
plt.xlabel('Time (s)')
plt.tight_layout()
plt.show()

