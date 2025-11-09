import numpy as np
from simulation import LVDT_mutual_inductance as LVDT_mutual_inductance

rat_amp = []
class Analysis:
    def __init__(self, save, default, offset, materials = None, input_excitation=None, design=None, filename=None, coil_dimensions = None,  parameter=None ):
        self.save = save
        self.default = default
        self.design = design
        self.offset = offset
        self.parameter = parameter
        self.des_dim = coil_dimensions
        self.filename = filename
        self.materials = materials if materials is not None else ['32 AWG', '32 AWG', 'N40']
        self.input_excitation = input_excitation if input_excitation is not None else [0.02, 10000, 0]

    def simulate(self):
        if self.default == 'yes':
            a = LVDT_mutual_inductance.Analysis1(save=False, default=self.default, offset=self.offset, materials1=self.materials, input_excitation=self.input_excitation, design_type=self.design)
        else:
            a = LVDT_mutual_inductance.Analysis1(save=False, default=self.default, offset=self.offset,materials1=self.materials, input_excitation=self.input_excitation, design_type=None, coil_dimensions1=self.des_dim, parameter1=self.parameter)
        b1 = a.simulate()
        # the inductance on one coil relative to the other is half of the net mutual inductance of both the coils
        M_UL = b1[0][1] / 2
        M_IL = b1[0][2] / 2
        M_IU = b1[0][0] / 2

        # time series
        Fs = 1000000  # sampling frequency in Hz
        T = 1 / Fs  # sampling period
        T_rec = 0.01  # recorded time in s
        Ndata = int(T_rec // T)  # number of data points, from T_rec = T * L
        t = np.arange(0, T_rec, T)
        f = 10000
        omega = 2 * np.pi * f
        I_in_amp = 0.020
        I_in_phi = 0.0 * np.pi
        mu_zero = 4 * np.pi * 10e-7

        L_in = b1[1][0]
        L_upout = b1[1][1]
        L_lowout = b1[1][2]

        # if outer coils in series
        # L_out = L_upout + L_lowout + 2*M_UL
        # L_out = L_upout + L_lowout +  M_UL   #without changing the mutual ind sign, i.e, M_IU is -ve and the rest is +ve
        # M_IO = (M_IU + M_IL)/2              #without changing the mutual ind sign, i.e, M_IU is -ve and the rest is +ve
        L_out = L_upout + L_lowout - (2 * M_UL)  # with changing the sign, i.e, all mutual ind are -ve
        M_IO = (M_IU - M_IL) / 1  # with changing the sign, i.e, all mutual ind are -ve
        L_out = b1[1][0] #for thr reversed LVDT
        L_in = L_upout + L_lowout - (2 * M_UL) #rev LVDT

        R_in = b1[3][0]
        R_upout = b1[3][1]
        R_lowout = b1[3][2]
        R_out = R_upout + R_lowout
        #R_out = b1[3][0]  #for rev LVDT
        R_in = R_upout + R_lowout #for rev

        X_in = omega * L_in
        X_upout = omega * L_upout
        X_lowout = omega * L_lowout
        X_out = omega * L_out
        X_out = omega * L_in  #for revLVDT
        X_in = omega * L_out  #revLVDT

        Z_in = np.sqrt(R_in ** 2 + X_in ** 2)
        Z_upout = np.sqrt(R_upout ** 2 + X_upout ** 2)
        Z_lowout = np.sqrt(R_lowout ** 2 + X_lowout ** 2)
        Z_out = np.sqrt(R_out ** 2 + X_out ** 2)

        Z_b_Tina = 2743.9 - 2501.6j  # with 10kohm: 2743.9 - 2501.6j, without 10Kohm: 2299.50 - 4221.47j
        #Z_b_Tina = 4743.9 - 2501.6j
        npoints = 100000
        rng = np.random.default_rng(12345)
        Z_b_real = Z_b_Tina.real * np.ones(npoints)  # Re[Z] from board
        signs = rng.random(size=npoints)
        for i in range(0, npoints):
            if signs[i] < 0.5: signs[i] = -1
            if signs[i] >= 0.5: signs[i] = 1

        Z_b_img = Z_b_Tina.imag * np.ones(npoints)  # Img[Z] from board
        Z_b_real[0] = Z_b_Tina.real
        Z_b_img[0] = Z_b_Tina.imag
        Z_b_real[1] = 1.0e6
        Z_b_img[1] = 0.0
        Z_b = Z_b_real + Z_b_img * 1j

        I_outs = np.zeros(npoints, dtype=complex)
        V_in_tots = np.zeros(npoints, dtype=complex)
        V_out_loads = np.zeros(npoints, dtype=complex)
        V_in_selfs = np.zeros(npoints, dtype=complex)
        V_in_inds = np.zeros(npoints, dtype=complex)
        V_out_selfs = np.zeros(npoints, dtype=complex)
        V_out_inds = np.zeros(npoints, dtype=complex)

        idx = -1
        amp_r = []
        for i in range(0, npoints):
            idx += 1
            R_out_tot = R_out + Z_b[i]  # add board resistance
            # try circuit analysis with complex numbers. Given I_in, what is I_upout?
            I_outs[idx] = (I_in_amp * omega * M_IO * 1j) / (omega * L_out * 1j + R_out_tot)
            V_in_tots[idx] = (R_in + omega * L_in * 1j) * I_in_amp - omega * M_IO * I_outs[idx] * 1j
            V_out_loads[idx] = (M_IO * I_in_amp - L_out * I_outs[idx]) * omega * 1j

            V_in_selfs[idx] = omega * L_in * I_in_amp * 1j
            V_in_inds[idx] = -omega * M_IO * I_outs[idx] * 1j
            V_out_selfs[idx] = -omega * L_out * I_outs[idx] * 1j
            V_out_inds[idx] = omega * M_IO * I_in_amp * 1j

            if idx == 0 or idx == 1:
                print(
                    f"Output voltage = {V_out_loads[idx]:.6f} amplitude = {np.abs(V_out_loads[idx]):.6f} phase = {np.angle(V_out_loads[idx]):.2f}")
                amp_r.append(np.abs(V_out_loads[idx]))

        ratio_amp = amp_r[0] / amp_r[1]
        print('correction factor', ratio_amp)
        rat_amp.append(ratio_amp)
        print('board impedance(ohms), magnitude:', Z_b_Tina, abs(Z_b_Tina))
        print('correction ratio :', rat_amp)

        if self.save:
            np.savez_compressed(self.filename, Design = b1[4], Input_config = b1[5], offset = b1[6], self_inductances_Inner_upper_lower = b1[1], mutual_ind_IU_UL_LI=b1[0],
                                k_factors=b1[2],board_impedance = Z_b_Tina, correction_factor = ratio_amp)

        return {'board_impedance': Z_b_Tina, 'correction_factor': ratio_amp}

