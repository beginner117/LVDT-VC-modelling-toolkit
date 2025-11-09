import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import shutil
import warnings
warnings.filterwarnings('ignore')

slopes = []; slopes_c = []; files_k = []
files = []; res = []; ind = []; correction = []
rea_err = []; rea_mean = []
ind_err = []; ind_mean = []
imp_err = []; imp_mean = []

a4 = ['ht13_rad20_dist38p8', 'ht14_rad20_dist37p8','ht18_dist34', 'ht18_dist34_innht11', 'ht19_dist33', 'ht19_dist33_innht11']
output_files=["C:\\Users\\kumar\\PycharmProjects\\lvdtsimulations\\femm_sim\\data\\A\\A_innht_{}.npz".format(i) for i in ['22', '24', '26', '28']] #'0.01', '0.02', '0.05', '0.1','0.2', '0.4', '0.6', '0.8', '1'
legends = ['radial gap-23mm\n(primary increment)', 'radial gap-23mm\n(secondary decrement)', 'radial gap-24mm\n(default)', 'radial gap-25mm\n(secondary increment)', 'radial gap-25mm\n(primary decrement)']
legends = ['22', '24', '26', '28']
#'23_inn12', '23_out34', '24_inn11_def', '25_out36', '25_inn10'   'radial gap-23mm\n(primary increment)', 'radial gap-23mm\n(secondary decrement)', 'radial gap-24mm\n(default)', 'radial gap-25mm\n(secondary increment)', 'radial gap-25mm\n(primary decrement)'
# 'dia_8', 'len_38', 'dia_10', 'len_42', 'dia_12'   'magnet diameter\n8mm', 'magnet length\n38mm', 'magnet diameter\n10mm (default)', 'magnet length\n42mm', 'magnet diameter\n12mm'
for i in range(0,len(output_files)):
    b = np.load(output_files[i], allow_pickle=True)
    files.append(b)
# for j in range(0,len(output_files_k)):
#     b_k = np.load(output_files_k[j], allow_pickle=True)
#     files_k.append(b_k)
#     correction.append(files_k[j]['correction_factor'])
correction = [1, 1, 1, 1, 1, 1, 1, 1]
print(correction)
n = len(output_files)
gain = 70.02

def plotter_func(func):
    def ploter(*args, **kwargs):
        plot_info = func(*args, **kwargs)
        plt.plot(plot_info['xaxis'], plot_info['yaxis'], 'o--', label = plot_info['label'])
        plt.xlabel(plot_info['xlabel'])
        plt.ylabel(plot_info['ylabel'])
        plt.title(plot_info['title'])
        plt.legend()
        plt.show()

# def slope_cal(func):
#     def wrapper(*args, **kwargs):
#         slope_info = func(*args, **kwargs)
#         m1, co1 = np.polyfit(slope_info['xaxis'], slope_info['yaxis'], 1)
#         print("slope and const :", m1, co1)
#         result = func(*args, **kwargs)
#         return result
#     return wrapper


class Lvdt():
    #@slope_cal
    def __init__(self, save, directory=None):
        self.sav = save
        self.directory = directory
        if self.directory and self.sav == 1:
                parent_dir = ""
                path1 = os.path.join(parent_dir, self.directory)
                self.path1 = path1
                os.mkdir(self.path1)
    def vol(self, par):
        for i in range(0,n):
            upp_out = np.array(files[i]["UOC_voltages"])
            low_out = np.array(files[i]["LOC_voltages"])
            inner = np.array(files[i]["IC_voltages"])
            if par == 'inner':
                m1, co1 = np.polyfit(np.array(files[i]["IC_positions"]), abs(inner), 1)
                plt.plot(np.array(files[i]["IC_positions"]), (inner), 'o-', label=legends[i])
            if par == 'upp_out':
                m1, co1 = np.polyfit(np.array(files[i]["IC_positions"]), abs(upp_out), 1)
                plt.plot(np.array(files[i]["IC_positions"]), (upp_out), 'o-', label=legends[i])
            if par == 'low_out':
                m1, co1 = np.polyfit(np.array(files[i]["IC_positions"]), (low_out), 1)
                plt.plot(np.array(files[i]["IC_positions"]), abs(low_out), 'o-', label=legends[i])
            if par == 'diff':
                m1, co1 = np.polyfit(np.array(files[i]["IC_positions"]), (abs(low_out)-abs(upp_out)), 1)
                plt.plot(np.array(files[i]["IC_positions"]), abs(abs(low_out)-abs(upp_out)), 'o-', label=legends[i])
        plt.ylabel('{} Coil Voltage [V] '.format(par))
        plt.xlabel('Inner Coil Position [mm]')
        plt.legend()
        if self.sav == 1:
            plt.savefig("upp_out.png")
            shutil.move("upp_out.png", self.path1)
        plt.show()
        print("slope and const :", m1, co1)
    #@plotter_func
    def info(self, param = None):
        inductance = np.zeros(n); impedance = np.zeros(n)
        out_dia = np.zeros(n); inn_dia = np.zeros(n)
        out_dc = np.zeros(n); inn_dc = np.zeros(n)
        for i in range(0,n):
            #design_type = files[i]["Design_type"]
            design_par = files[i]["Design_parameters"]
            input_par = files[i]["Input_parameters"]
            input_coil = files[i]["Innercoil_config"]; inn_pos = np.array(files[i]["IC_positions"])
            upp_out = np.array(files[i]["UOC_voltages"]); low_out = np.array(files[i]["LOC_voltages"])
            inn_vol = np.array(files[i]["IC_voltages"]); inn_cur = np.array(files[i]["IC_currents"])
            out_sig = abs(np.array(files[i]["UOC_voltages"])) - abs(np.array(files[i]["LOC_voltages"]))
            norm_sig = out_sig / abs(inn_vol); norm_sig_c = out_sig / abs(inn_cur)
            m_fem, co_fem = np.polyfit(inn_pos, norm_sig * gain * correction[i], 1)  # [8:13]
            m_fem_c, co_fem_c = np.polyfit(inn_pos, norm_sig_c, 1)
            sim_fit = (m_fem * np.array(inn_pos)) + (co_fem); sim_fit_c = (abs(m_fem_c) * np.array(inn_pos)) + (co_fem_c)
            relerr_fem = (abs(sim_fit - norm_sig * gain * correction[i]) / abs(norm_sig * gain * correction[i])) * (100)
            relerr_fem_c = ((abs(sim_fit_c - (norm_sig_c))) / abs(norm_sig_c)) * (100)
            fiterr_fem = (sim_fit - norm_sig)
            indu = np.array(files[i]["IC_flux"]) / np.array(inn_cur)
            inductance[i] = abs(sum(indu * 1000) / len(indu))
            resi = np.array(files[i]["IC_voltages"]) / np.array(files[i]["IC_currents"])
            impedance[i] = abs(sum(resi) / len(resi))
            g1 = files[i]['Input_parameters'].item(); g2 = files[i]['Inn_Uppout_Lowout_DCR_as_per_catalog']
            out_dc[i] = g2[1]; inn_dc[i] = g2[0]
            print( design_par,'\n', input_par, '\n', inn_vol, '\n', inn_cur)
            #print('outer\n'); print(upp_out, '\n', low_out)

        if param == 'signal':
            return {'xaxis':inn_pos, 'yaxis':out_sig, 'xlabel':'Inner coil position [mm]', 'ylabel':'Outer Coil signal [V]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'norm_signal':
            return {'xaxis':inn_pos, 'yaxis':norm_sig, 'xlabel':'Inner coil position [mm]', 'ylabel':'Normalised Outer Coil signal [V/v]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'rel_error':
            return {'xaxis':inn_pos, 'yaxis':abs(relerr_fem), 'xlabel':'Inner coil position [mm]', 'ylabel':'Relative error [%]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'slope':
            return {'xaxis':legends, 'yaxis':slopes, 'xlabel':'Inner coil position [mm]', 'ylabel':'response slope [V/mmV]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'slope_c':
            return {'xaxis':legends, 'yaxis':slopes_c, 'xlabel':'Inner coil position [mm]', 'ylabel':'response slope [V/mmA]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'inn_inductance':
            return {'xaxis':legends, 'yaxis':inductance, 'xlabel':'Inner coil position [mm]', 'ylabel':'Inner coil inductance (Flux/current) [mH]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
        if param == 'out_dcr':
            return {'xaxis':legends, 'yaxis':out_dc, 'xlabel':'Inner coil position [mm]', 'ylabel':'Outer coil DC resistance [Ω]',
                    'title':'top up IP, Sensitivity, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)', 'label':legends}
    def norm_sig(self, param = None):
        for i in range(0,n):
            inn_pos = np.array(files[i]["IC_positions"]); inn_sig = (np.array(files[i]["IC_voltages"]))
            uoc_cur = np.array(files[i]["UOC_currents"]); loc_cur = np.array(files[i]["LOC_currents"])
            uoc_vol = np.array(files[i]["UOC_voltages"]); loc_vol = np.array(files[i]["LOC_voltages"])
            out_sig = abs(np.array(files[i]["UOC_voltages"])) - abs(np.array(files[i]["LOC_voltages"]))
            norm_sig = out_sig / abs(np.array(files[i]["IC_voltages"])); norm_sig_c = out_sig / abs(np.array(files[i]["IC_currents"]))
            print(inn_sig, out_sig, norm_sig)
            plt.plot(np.array(files[i]["IC_positions"][60:140]), (norm_sig[60:140]), 'o--', label=legends[i])
        #plt.legend()
        plt.grid()
        plt.ylabel(r'Normalised LVDT response $[\frac{{V}^{out}}{{V}^{in}}]$', fontsize=13, fontname='Arial')
        plt.xlabel('Primary Coil Position relative to the secondary [in mm]', fontsize=13, fontname='Arial')
        plt.title(r'LVDT response with 20 mA, 10 kHz sinusoid excitation' + '\n' + 'ETpathfinder design type : A' , fontsize=14, fontname='Arial')
        plt.tight_layout()
        #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\lvdt_sim_longrange.pdf", format='pdf')
        if self.sav == 1:
            plt.savefig("norm_sig.png")
            shutil.move("norm_sig.png", self.path1)
        plt.show()
    def norm_rev_fit(self, par):
        for i in range(0, n):
            inn_pos = np.array(files[i]["IC_positions"]); inn_sig = (np.array(files[i]["IC_voltages"]))
            uoc_cur = np.array(files[i]["UOC_currents"]); loc_cur = np.array(files[i]["LOC_currents"])
            uoc_vol = np.array(files[i]["UOC_voltages"]); loc_vol = np.array(files[i]["LOC_voltages"])
            out_sig = abs(np.array(files[i]["UOC_voltages"])) - abs(np.array(files[i]["LOC_voltages"]))
            norm_sig_c = abs(inn_sig) / (2*abs(uoc_vol))
            norm_sig = (inn_sig) / uoc_vol
            m_fem_c, co_fem_c = np.polyfit(inn_pos[11:], norm_sig_c[11:], 1)
            sim_fit_c = (abs(m_fem_c) * np.array(inn_pos)) + (co_fem_c)
            if par == 'signal':
                plt.plot(inn_pos, sim_fit_c, 'o-', label=legends[i])
            if par == 'slope':
                #print("femm signal slope, constant :", abs(m_fem), co_fem)
                print("femm signal with current slope, constant :", abs(m_fem_c), co_fem_c)
                #slopes.append(m_fem)
                slopes_c.append(m_fem_c)
        print('slopes v/mmA', slopes_c)
        plt.ylabel(r'Fitted normalised LVDT response $[\frac{{V}}{{A}}]$')
        plt.xlabel('Inner Coil Position[in mm] relative to outer coil ')
        plt.title(r'Reverse LVDT Sensitivity $[\frac{{V}^{out}}{{A}^{in}}]$ with 20mA sinusoid excitation' + '\n' + '( sim range:±5mm,0.5mm step, full fit)')
        plt.legend(title='excitation frequency')
        if self.sav == 1:
            plt.savefig("normfiterr.png")
            shutil.move("normfiterr.png", self.path1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def norm_fit(self, par:str):
        markers = ['o--', 'D--', '*--', 'P--', 'H--']
        for i in range(0,n):
            inn_pos = np.array(files[i]["IC_positions"]); inn_sig = (np.array(files[i]["IC_voltages"]))
            uoc_cur = np.array(files[i]["UOC_currents"]); loc_cur = np.array(files[i]["LOC_currents"])
            uoc_vol = np.array(files[i]["UOC_voltages"]); loc_vol = np.array(files[i]["LOC_voltages"])
            out_sig = abs(np.array(files[i]["UOC_voltages"])) - abs(np.array(files[i]["LOC_voltages"]))
            norm_sig = out_sig /abs(np.array(files[i]["IC_voltages"]))
            norm_sig_c = out_sig / abs(np.array(files[i]["IC_currents"]))

            m_fem, co_fem = np.polyfit(inn_pos[8:13], norm_sig[8:13]*gain*correction[i], 1)
            m_fem_c, co_fem_c = np.polyfit(inn_pos[8:13], norm_sig_c[8:13], 1)
            sim_fit = (m_fem * np.array(inn_pos))+ (co_fem)
            sim_fit_c = (abs(m_fem_c) * np.array(inn_pos))+ (co_fem_c)
            relerr_fem = (abs(sim_fit - norm_sig*gain*correction[i]) / abs(norm_sig*gain*correction[i])) * (100)
            relerr_fem_c = ((abs(sim_fit_c - (norm_sig_c))) / abs(norm_sig_c)) * (100)
            fiterr_fem = (sim_fit - norm_sig)
            pos_upd = norm_sig*gain/abs(m_fem)
            pos_dri = abs(inn_pos) - abs(pos_upd)
            if par == 'signal':
                plt.plot(inn_pos, norm_sig_c, '.', label='data')
                plt.plot(inn_pos, sim_fit_c, label='fit')
            if par == 'rel_error' :
                plt.plot(np.delete(inn_pos, [10]), np.delete(abs(relerr_fem_c), [10]), markers[i], label=legends[i])
                plt.ylim(0, 2)
            if par == 'error' :
                plt.plot(inn_pos, (sim_fit - norm_sig)*0.02, 'o-', label=legends[i])
            if par == 'drift':
                plt.plot(inn_pos, pos_dri * 1000, 'o--', label = 'simulation')
            if par == 'slope':
                print("femm signal slope, constant :", abs(m_fem), co_fem)
                print("femm signal with current slope, constant :", abs(m_fem_c), co_fem_c)
                slopes.append(m_fem)
                slopes_c.append(m_fem_c)
        if par == 'signal' :
            plt.ylabel(r'Fitted normalised LVDT response $[\frac{{V}}{{A}}]$')
            plt.xlabel('Primary Coil Position relative to outer coil [in mm]')
            plt.title(r'LVDT Sensitivity $[\frac{{V}^{out}}{{A}^{in}}]$ with 20 mA, 10 kHz sinusoid excitation' + '\n' + '(type-A, ±1mm fit)')
            plt.grid(b=True)
            plt.legend()
            plt.xticks(rotation=0, fontsize=14)
            plt.tight_layout()
            #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\typeA1_32AWG_sens_fit.pdf", format = 'pdf')
        elif par == 'rel_error':
            #plt.ylim(0, 1)
            plt.ylabel('Relative error [%]', fontsize=14, fontname='Arial')  # [$\dfrac{abs(fit error)}{actual}$]
            plt.xlabel('Primary coil position relative to the secondary [in mm]', fontsize=14, fontname='Arial')
            plt.title(r'LVDT linearity with 20 mA, 10 kHz sinusoid excitation' + '\n' + '(fit range : ±1 mm)')
            plt.grid(b = True)
            plt.legend(title = 'Primary coil\nheight (in mm)')
            plt.xticks(rotation=0, fontsize=14)
            plt.tight_layout()
            plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\remade\\typeA1_32awg_innht_lin.pdf", format = 'pdf')
        elif par == 'error':
            plt.ylabel('Error [V]')
            plt.xlabel('Inner Coil Position[in mm] relative to outer coil ')
            plt.title(r'Error (fit - actual) [V] with 20mA-10Khz sinusoid excitation' + '\n' + '(type-A, sim range:±5mm,0.5mm step, full fit)')
        elif par == 'drift':
            plt.ylabel('Position drift [μm]', fontsize=14, fontname='Arial')
            plt.xlabel('Primary Coil Position relative to the secondary [in mm]', fontsize=14, fontname='Arial')
            plt.title('Position drift due to relative fit error\n(20mA-10kHz excitation, ±1mm fit)')
            plt.grid(b=True)
            plt.legend()
            plt.xticks(rotation=0, fontsize=14)
            plt.tight_layout()
            #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\typeA1_32awg_drift.pdf", format = 'pdf')
        elif par == 'slope':
            plt.plot(legends, (-slopes_c[1]+np.array(slopes_c))*100/slopes_c[1], "o--", label='simulation')
            plt.ylabel('Sensitivity change [%]', fontsize=14, fontname='Arial')
            plt.xlabel('Inner coil height (in mm)', fontsize=14, fontname='Arial')
            plt.title(r'Sensitivities $[\frac{{V}^{out}}{mm.{A}^{in}}]$ with 20 mA, 10 kHz sinusoid excitation' + '\n' +'(sim range : ±5 mm, fit range : ±1 mm)')
            plt.grid(b = True)
            plt.xticks(rotation=25, fontsize=10)
            plt.tight_layout()
            #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\remade\\typeA1_32awg_innht_slope.pdf", format = 'pdf')
        #plt.ylim(0,10)
        #plt.legend()
        if self.sav == 1:
            plt.savefig("normfiterr.png")
            shutil.move("normfiterr.png", self.path1)
        #plt.grid()
        plt.tight_layout()
        plt.show()
    def resistance(self, par:str):
        inductance = np.zeros(n); impedance = np.zeros(n)
        out_dia = np.zeros(n); inn_dia = np.zeros(n)
        out_dc = np.zeros(n); inn_dc = np.zeros(n)
        for i in range(0,n):
            indu = np.array(files[i]["IC_flux"])/np.array(files[i]["IC_currents"])
            inductance[i] = abs(sum(indu*1000)/len(indu))
            resi = np.array(files[i]["IC_voltages"])/np.array(files[i]["IC_currents"])
            impedance[i] = abs(sum(resi) / len(resi))
            g1 = files[i]['Input_parameters'].item()
            g2 = files[i]['Inn_Uppout_Lowout_DCR_as_per_catalog']
            out_dc[i] = g2[1]; inn_dc[i] = g2[0]

        #print(abs(impedance))
        if par == "inductance" :
            print(inductance)
            plt.plot(legends, inductance, "o-")
            plt.ylabel("Inner coil inductance (Flux/current) [mH]")
        elif par == "DC_resistance" :
            plt.plot(legends, out_dc*2, "o-")
            plt.ylabel("Outer coil DC resistance [Ω]")
            #plt.ylabel("Inner coil DC resistance [Ω]")
        else:
            plt.plot(legends, impedance, "o-")
            plt.ylabel('Inner coil impedance [Ω]')
        if self.sav == 1:
            plt.savefig("inn_ind.png")
            shutil.move("inn_ind.png", self.path1)
        plt.xlabel("out coil ht_out coil dist(total ht)\n[in mm]")
        plt.grid()
        plt.title('top up IP, Resistance, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)')
        plt.tight_layout()
        plt.show()
    def lin_imp(self):
        for i in range(0,n):
            gain = 65
            inn_pos = np.array(files[i]["IC_positions"])
            out_sig = abs(np.array(files[i]["UOC_voltages"])) - abs(np.array(files[i]["LOC_voltages"]))
            norm_sig = out_sig / abs(np.array(files[i]["IC_voltages"]))
            m_fem, co_fem = np.polyfit(inn_pos, norm_sig*gain, 1)
            print("femm signal slope :", m_fem, co_fem)
            slopes.append(m_fem)
            sim_fit = m_fem * np.array(inn_pos) + co_fem
            relerr_fem = ((abs(sim_fit - norm_sig)) / abs(norm_sig)) * 100
        ref_slope = []
        plt.plot(legends, (slopes-slopes[3])*100/slopes[3], "o--")
        #plt.xlabel('Inner Coil Position [mm]')
        plt.ylabel('slope improvement [%]')
        plt.xlabel('type of coil')
        #plt.ylim(-33, 33)
        plt.legend()
        if self.sav == 1:
            plt.savefig("linfit.png")
            shutil.move("linfit.png", self.path1)
        plt.show()
    def power(self):
        for i in range(0,n):
            power = files[i]['IC_currents']*files[i]['IC_voltages']
            plt.plot(np.array(files[i]["IC_positions"]), power, "o--", label = legends[i])
        plt.ylabel('Inner coil Power [W]')
        plt.xlabel('Inner Coil Position [mm]')
        plt.legend()
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.show()

class VC:
    def __init__(self, save, directory=None):
        self.sav = save
        self.directory = directory
        if self.directory and self.sav == 1:
                parent_dir = ""
                path1 = os.path.join(parent_dir, self.directory)
                self.path1 = path1
                os.mkdir(self.path1)
    def info(self):
        for i in range(0,n):
            #forces = files[i]["Mag_forces"]
            #design_par = files[i]["Design"]
            input_par = files[i]["Input_parameters"]
            print(input_par)
    def force(self, para=None):
        markers = ['o--', '*--', '.--', 'H--', '*--']
        for i in range(0,n):
            inn_pos = np.array(files[i]["IC_positions"])
            #inn_pos = np.array(files[i]['UOC_positions'])
            coil_force2 = np.zeros(len(inn_pos))
            mag_force = (np.array(files[i]["Mag_forces"]))
            coil_force1 = (np.array(files[i]["UOC_forces"]))
            coil_force2 = (np.array(files[i]["LOC_forces"]))
            coil_force = coil_force1 + coil_force2
            #coil_force = (np.array(files[i]["IC_forces"]))
            currents = np.array(files[i]["UOC_currents"])
            if para == 'coil_norm':
                plt.plot(inn_pos, (coil_force)/currents, markers[i], label = legends[i])
                plt.ylabel(' Normalised coil Force [N/A]', fontsize=13, fontname='Arial')
                plt.title('Actuation forces \n [ETpf design type:I, 1A DC excitation]', fontsize=14, fontname='Arial')
                plt.xlabel('Primary Coil(or magnet) Position relative to the outer coil[mm]', fontsize=13, fontname='Arial')
                plt.xticks(rotation=0, fontsize=14)
                plt.grid(b=True)
                plt.tight_layout()
                #plt.legend(title = 'Input\ncurrent')
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\H_vc_for.pdf", format = 'pdf')
            if para == 'mag_norm':
                plt.plot(inn_pos, (mag_force)/currents, markers[i], label = legends[i])
                plt.ylabel(' Normalised magnet Force [N/A]', fontsize=14, fontname='Arial')
                plt.title('Magnet Forces with varying excitations \n [type-I]')
                plt.xlabel('Primary Coil(or magnet) Position relative to the outer coil[mm]', fontsize=14, fontname='Arial')
                plt.title('Magnet Forces \n [type-I]')
                plt.grid(b=True)
                plt.tight_layout()
                plt.legend(title = 'Input\ncurrent')
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\typeI_magfor_high_inputs.pdf", format='pdf')
            if para == 'mag':
                plt.plot(inn_pos, mag_force, 'o-', label = legends[i])
                plt.ylabel('Magnet Force [N]')
                plt.title('Magnet Forces \n [magnet forces]')
            if para == 'coil':
                plt.plot(inn_pos, coil_force, 'o-', label = legends[i])
                plt.ylabel('Coil Force [N]')
                plt.title('Sum of Outer Coil Forces \n [coil forces]')
            if para == 'stability':
                plt.plot(inn_pos, abs(coil_force)*100/max(abs(coil_force)), 'o--', label=legends[i])
                plt.ylabel(' VC force/maximum VC force [%]')
                plt.title(r'VC force stability with 1A, DC excitation' + '\n' + '(ETpf design type-B, DC excitation)')
                plt.grid(True)
                #plt.legend(title='Secondary coil \n height (in mm)')
                plt.tight_layout()
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\remade\\B_vc_stab.pdf", format = 'pdf')
            if para == 'diff':
                plt.plot(inn_pos, abs(abs(mag_force)-abs(coil_force))/currents, 'o-', label = legends[i])
                plt.ylabel('absolute force difference (magnet force-coil force) [N/A]')
                #plt.ylim(-0.05, 0.2)
                plt.title('Forces difference [Type : I with type A magnet,] \n RS-wire')
        plt.xlabel('Magnet Position relative to the outer coil [mm]')
        #plt.legend(title = 'Input\ncurrent')
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    def force_fit(self, para=None):
        forc = []; data_p = np.zeros(n)
        markers = ['o-', '*-', 'D-', 'H--', 'P--']
        print('test')
        for i in range(0, n):
            inn_pos = np.array(files[i]["IC_positions"])
            #inn_pos = np.array(files[i]['UOC_positions'])
            mag_force = (np.array(files[i]["Mag_forces"]))
            coil_force1 = (np.array(files[i]["UOC_forces"]))
            coil_force2 = (np.array(files[i]["LOC_forces"]))
            #coil_force2 = np.zeros(len(inn_pos))
            print(mag_force, inn_pos)
            coil_force = coil_force1+coil_force2
            currents = np.array(files[i]["UOC_currents"])
            p1 = 0; p2 = 21
            a1, a2, a3 = np.polyfit(inn_pos, abs(coil_force),2)
            fit_for = (a1*(inn_pos**2))+(a2*inn_pos)+a3
            fit_for_sm = (a1 * (np.linspace(-2.5, 2.5, 1000)** 2)) + (a2 * (np.linspace(-2.5, 2.5, 1000))) + a3
            b1, b2, b3 = np.polyfit(inn_pos, abs(mag_force), 2)
            fit_for_mag = (b1 * (inn_pos ** 2)) + (b2 * inn_pos) + b3
            data_p[i] = max(fit_for_mag)

            if para == 'mag_norm':
                plt.plot(inn_pos, fit_for_mag/currents, 'o-', label = legends[i])
                plt.ylabel(' Fitted normalised magnet Force [N/A]', fontsize=14, fontname='Arial')
                plt.title('VC force with varying primary coil height' + '\n' + '(1A-DC excitation, type-G, full fit)')
                plt.xlabel('Primary Coil(or magnet) Position relative to the outer coil[mm]', fontsize=14, fontname='Arial')
                plt.grid(b = True)
                plt.tight_layout()
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\paper\\typeG_innrad.pdf",format='pdf')
            if para == 'coil_norm':
                plt.plot(inn_pos, abs(coil_force) / currents, 'o', label='data')
                #plt.plot((np.linspace(-2.5, 2.5, 1000)), fit_for_sm, label = 'fit')
                plt.ylabel('Normalised coil Force [N/A]', fontsize=14, fontname='Arial')
                plt.title('Outer coil forces \n [type-G, sim range : ±2.5 mm, full fit]')
                plt.xlabel('Primary Coil (or magnet) Position relative to the outer coil [mm]', fontsize=14, fontname='Arial')
                #plt.title('Outer Coil Forces \n [full fit]')
                plt.xticks(rotation = 0, fontsize = 14)
                plt.grid(True)
                plt.tight_layout()
                plt.legend()
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\paper\\typeG_coilfor.pdf", format='pdf')

            if para == 'diff':
                plt.plot(inn_pos, (mag_force+coil_force)/currents, 'o-', label = legends[i])
                plt.ylabel('norm force difference (magnet force+coil force) [N/A]')
                plt.title('Force difference \n [Type : A, full fit, wire - 32 AWG]')
            if para == 'error':
                plt.plot(inn_pos[p1:p2], (abs(fit_for[p1:p2])-abs(coil_force[p1:p2]))*100/abs(coil_force[p1:p2]), 'o-', label = legends[i])
                plt.ylabel('relative fit force error [%]')
                plt.title(r'VC fit error with 1A-DC excitation' + '\n' + '( sim range:±5mm,0.5mm step, full fit)')
            if para == 'stability':
                plt.plot(inn_pos, fit_for*100/max(fit_for), markers[i], label=legends[i])
                # plt.plot((np.linspace(-2.5, 2.5, 1000)), fit_for_sm*100/max(fit_for))
                plt.ylabel(' Fitted force stability [%]', fontsize=14, fontname='Arial')
                plt.xlabel('Primary Coil(or magnet) Position relative to the outer coil[mm]', fontsize=14, fontname='Arial')
                plt.title(r'VC force stability with 1A, DC excitation' + '\n' + '(full fit)')
                plt.grid(b = True)
                plt.xticks(rotation=0, fontsize=14)
                plt.legend(title = 'outer coil\ndistance (in mm)')
                plt.tight_layout()
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\remade\\typeA1_32awg_vc_dist_stab.pdf", format = 'pdf')
            if para == 'rel_error':
                plt.plot(inn_pos, (abs(fit_for-coil_force)/abs(coil_force))*100, 'o', label = legends[i])
                #plt.ylim(0, 1000)
                plt.ylabel('relative fit force error [%]')
                plt.title('Relative error \n [Type-A,, 1A DC excitation]')
                plt.xlabel('Primary Coil Position relative to the outer coil[mm]', fontsize=14, fontname='Arial')
                plt.grid(b=True)
                plt.xticks(rotation=0, fontsize=14)
                #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\typeA1_vc_fiterr.pdf", format='pdf')
        if para == 'slopes':
            plt.plot(legends, (data_p-data_p[1])*100/data_p[1], 'o--')
            #plt.plot(legends, data_p, 'o--')
            plt.ylabel('Maximum force change [%]', fontsize=14, fontname='Arial')
            plt.xlabel('Outer coil distance (in mm)', fontsize=14, fontname='Arial')
            plt.title('Maximum actuation force with 1A, DC excitation\n(sim range : ±5mm, full fit)', fontsize=14, fontname='Arial')
            plt.xticks(rotation=25, fontsize=12)
            plt.grid(True)
            #plt.legend(title='Simulation')
            plt.tight_layout()
            #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\remade\\typeA1_32awg_vc_outdist_slope.pdf", format = 'pdf')
            #plt.xlabel()
        #plt.xlabel('Primary Coil(or magnet) Position relative to the outer coil[mm]', fontsize=14, fontname='Arial')
        # plt.ylabel(r'(updated force/default force)*100   [%]')
        # plt.title('VC Force improvement with diameter \n 1A DC excitation')
        #plt.legend(title = 'input\ncurrent')
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.tight_layout()
        plt.show()
        print(forc)
    def linearity(self, par:list):

        for j in range(len(par)):
            force = []
            for i in range(0,n):
                currents = np.array(files[i]["UOC_currents"])
                mag_force = abs(np.array(files[i]["Mag_forces"]))
                force.append(mag_force[par[j]])
            plt.plot(legends, force, 'o--', label = par[j]-40)
        #plt.xticks(rotation = 15)
        plt.xlabel('outer coil current')
        plt.ylabel('Force [N]')
        plt.title('force at various positions ')
        plt.legend(title = 'position(mm)')
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.grid()
        plt.show()
    def stability(self):
        for i in range(0,n):
            #coil_force1 = (np.array(files[i]["UOC_forces"]))
            #coil_force2 = (np.array(files[i]["LOC_forces"]))
            #coil_force2 = np.zeros(len(files[i]["UOC_positions"]))
            #coil_force = coil_force1 + coil_force2
            inn_pos = np.array(files[i]["IC_positions"])
            renormalised_forces = (abs(np.array(files[i]["Mag_forces"]))/max(abs(np.array(files[i]["Mag_forces"]))))*100
            #renormalised_forces = (abs(coil_force) / max(abs(coil_force))) * 100
            a1, a2, a3 = np.polyfit(inn_pos, renormalised_forces, 2)
            fit_renormalised_forces = (a1*(inn_pos**2))+(a2*(inn_pos))+a3
            plt.plot(inn_pos, fit_renormalised_forces, "o-", label = 'simulation')
        plt.ylabel('Fitted force stability [%]')
        plt.xlabel('Inner Coil(or magnet) Position relative to outer coil[mm]')
        plt.legend()
        plt.grid()
        plt.title(r'VC force Stability' + '\n' + '( sim range:±5mm,0.5mm step, full fit)')
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.show()
    def resistance(self, par:str):
        inductance = np.zeros(n); impedance = np.zeros(n)
        out_dia = np.zeros(n); inn_dia = np.zeros(n)
        out_dc = np.zeros(n); inn_dc = np.zeros(n)
        for i in range(0,n):
            indu = np.array(files[i]["IC_flux"])/np.array(files[i]["IC_currents"])
            inductance[i] = abs(sum(indu*1000)/len(indu))
            resi = np.array(files[i]["UOC_voltages"])/np.array(files[i]["UOC_currents"])
            impedance[i] = abs(sum(resi) / len(resi))
            g1 = files[i]['Input_parameters'].item()
            g2 = files[i]['Inn_Uppout_Lowout_DCR_as_per_catalog']
            out_dc[i] = g2[1]+g2[2]; inn_dc[i] = g2[0]
        if par == "inductance" :
            print(inductance)
            plt.plot(legends, inductance, "o-")
            plt.ylabel("Inner coil inductance (Flux/current) [mH]")
        elif par == "DC_resistance" :
            plt.plot([1, 2], out_dc, "o-")
            plt.ylabel("Outer coil DC resistance [Ω]")
        else:
            plt.plot(legends, impedance, "o-")
            plt.ylabel('Inner coil impedance [Ω]')
        if self.sav == 1:
            plt.savefig("inn_ind.png")
            shutil.move("inn_ind.png", self.path1)
        plt.xlabel("Outer coil height (mm)")
        plt.grid()
        plt.title('top up IP, Resistance, gain:70.02\n(20mA excitation, sim range:±5mm,0.25mm step, full fit)')
        plt.tight_layout()
        plt.show()
    def power(self):
        po = []
        for i in range(0,n):
            power = (files[i]['LOC_currents']*files[i]['LOC_voltages'])/1000000
            po.append(max(power))
            plt.plot(np.array(files[i]["IC_positions"]), power, "o--", label = legends[i])
        plt.ylabel('Lower out coil Power [W]')
        plt.xlabel('Inner Coil Position [mm]')
        plt.legend()
        if self.sav == 1:
            plt.savefig("Inn_vol.png")
            shutil.move("Inn_vol.png", self.path1)
        plt.show()
        print(po)




