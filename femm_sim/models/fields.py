import femm
import sys
import numpy as np
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class Coil_magfield:

    def __init__(self, r_offset, angle, freq, current, radius, coil_height, turns_pr_layer, layers, insulated_wire_thickness, position, upper_uppend=None,lower_uppend = None):
        self.upper_uppend = upper_uppend
        self.lower_uppend = lower_uppend
        self.r_offset = r_offset
        self.radius = radius
        self.position = position
        self.turns_pr_layer = turns_pr_layer
        self.layers = layers
        self.wire = insulated_wire_thickness
        self.coil = coil_height
        self.current = current
        self.angle = angle
        self.freq = freq
        #self.res = res

    def forces(self, mag_len, mag_dia, current):
        gri_x = [];mag_fie_x = [];mag_fie_y = [];gri_y = []
        def_force = [];imp_force = [];rot_x = [];rot_y = [];math_model_force = []
        for item in range(0, self.layers):
            for j in range(0, self.turns_pr_layer):
                grid_pt = [self.radius+(self.wire*(item+1)), (self.position+(self.coil/2))-(j*self.wire)]
                #print(grid_pt[0])
                #print(type(grid_pt[0]))
                b_field = femm.mo_getb(grid_pt[0], grid_pt[1])
                gri_x.append(grid_pt[0])
                gri_y.append(grid_pt[1])
                mag_fie_x.append(b_field[0])
                mag_fie_y.append(b_field[1])

                g = (2*np.pi*grid_pt[0]*self.current*b_field[0])/1000
                def_force.append(g)
                theta = (self.angle/180)*np.pi
                rotMatrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
                c = np.dot(rotMatrix, np.array(b_field))
                rot_x.append(c[0])
                rot_y.append(c[1])
                f = (2*np.pi*c[0]*self.current*b_field[0])/1000
                imp_force.append(f)

                mu_o = 1.256 * (10 ** -6)
                m = 969969

                # def func(rad, theta1):
                #     p1 = mag_len / 2 - grid_pt[1]
                #     p2 = mag_len / 2 + grid_pt[1]
                #     fis = (2 * rad * (grid_pt[0] - rad * np.cos(theta1))) / 2 * (
                #             (rad ** 2) + (p1 ** 2) + (grid_pt[0] ** 2) - (
                #             2 * rad * grid_pt[0] * np.cos(theta1))) ** 1.5
                #     sec = (2 * rad * (grid_pt[0] - rad * np.cos(theta1))) / 2 * (
                #             (rad ** 2) + (p2 ** 2) + (grid_pt[0] ** 2) - (
                #             2 * rad * grid_pt[0] * np.cos(theta1))) ** 1.5
                #     return sec - fis
                #
                # res = integrate.dblquad(func, 0, mag_dia / 2, 0, 2 * np.pi)
                # v1 = (res[0] * mu_o * m * 0.25 / np.pi) / 10 ** 8
                # v11 = 2 * np.pi * grid_pt[0] * v1 * current / 1000
                # math_model_force.append(v11)
        #print('default force :', sum(def_force), 'updated force:', sum(imp_force))
        return [sum(def_force), sum(imp_force)]

class Force_field:
    def __init__(self, B_field_file):
        self.field_file = B_field_file
        self.file = np.load(self.field_file, allow_pickle=True)
    def forces(self, x_offset, out_radius, out_dist,out_ht, turns_pr_layer, layers,wire_dia, insulated_thickness):
        for layer in range(0, layers):
            for turn in range(0, turns_pr_layer):
                grid_pt_upp = [out_radius+(layer*(wire_dia + 2*insulated_thickness)), (out_dist+out_ht)/2 - (turn*(wire_dia+2*insulated_thickness))]
                grid_pt_low = [out_radius+(layer*(wire_dia + 2*insulated_thickness)), -(out_dist+out_ht)/2 + (turn*(wire_dia+2*insulated_thickness))]

                b_field_upp = femm.mo_getb(grid_pt_upp[0], grid_pt_upp[1])
                b_field_low = femm.mo_getb(grid_pt_low[0], grid_pt_low[1])

class B_field:
    """
    Represents a magnetic field calculation in a cylindrical coordinate system.
    Args:
        r_max (float): Maximum radial distance in mm.
        z_max (float): Maximum axial distance in mm.
        r_grid (float): Radial grid spacing in mm.
        z_grid (float): Axial grid spacing in mm.
        filename (str, optional): Name of the file to save results (default: None).
        design_type (str, optional): Type of magnetic field design (default: None).
        design_parameters (dict, optional): Parameters related to the magnetic field design (default: None).
        input_parameters (dict, optional): Input parameters for the calculation (default: None).
        inner_voltage (float, optional): Voltage applied to the inner coil (default: None).
        inner_flux (float, optional): Magnetic flux in the inner coil (default: None).
        outer_voltage (float, optional): Voltage applied to the upper(assuming the symmetric lower outer coil) outer coil (default: None).
        outer_flux (float, optional): Magnetic flux in the upper(assuming the symmetric lower outer coil) outer coil (default: None).
    Methods:
        calculate(): Computes the magnetic field distribution and saves results if a filename is provided.
    """
    def __init__(self, r_max,z_max, r_grid, z_grid, filename=None,design_type=None,design_parameters=None, input_parameters=None,
                 inner_voltage=None, inner_flux=None, outer_voltage=None, outer_flux=None):
        self.r_max = r_max; self.z_max = z_max
        self.dr = r_grid; self.dz = z_grid
        self.coil_config = design_parameters
        self.input_parameters = input_parameters
        self.inner_voltage = inner_voltage ; self.inner_flux = inner_flux
        self.outer_voltage = outer_voltage ; self.outer_flux = outer_flux
        self.filename = filename
    def calculate(self):
        """
        Computes the magnetic field distribution.
        Saved file contains information about the radial and axial vectors, step sizes for grid spacing, matrices of B-field values (with r and z components), details about the input parameters and coil-related information such as voltages and fluxes.
        :return: list: containing the B-field vectors (B_r + i*B_z) for each grid point.
        """
        r_vec = np.arange(0, self.r_max+self.dr, self.dr, dtype = np.double) #position vectors and flux
        z_vec = np.arange(0, self.z_max+self.dz, self.dz, dtype = np.double) #z_vec will be mirrored about z=0 later
        print(len(z_vec), z_vec[1], r_vec[1])
        b_vec = np.zeros((len(z_vec), len(r_vec), 2), dtype = np.double).astype(complex) # Constructing the matrix of B field vectors (B_r,B_z)
        # Computing the B field in the r,z-plane
        for i in range(len(z_vec)):
            for j in range(len(r_vec)):
                if j < 5:
                    print(r_vec[j], z_vec[i])
                b_vec[i, j, :] = femm.mo_getb(r_vec[j], z_vec[i])

        b_vec_z = np.real(b_vec[:, :, 1])  #b_mat_z, Matrix of B(r,z) field with only z components (index: 1): only relevant data for flux computation
        b_vec_r = np.real(b_vec[:, :, 0])   #b_mat_r, Matrix of B(r,z) field with only r components (index: 0)

        if self.filename:
            np.savez_compressed(self.filename, radial_vectors = r_vec, z_vectors = z_vec, radial_step = self.dr, z_step = self.dz,
                                mag_field_z = b_vec_z, mag_field_r = b_vec_r,
                                Input_parameters = self.input_parameters, Coils_config = self.coil_config,
                                innercoil_voltage = self.inner_voltage, innercoil_flux = self.inner_flux,
                                upp_outercoil_voltage = self.outer_voltage, upp_outercoil_flux = self.outer_flux)
        return b_vec

class Flux:
    def __init__(self, datafile, x_offset,  flux_file=None, save = None, type=None, coil_wiretype=None, wire_thickness=None):
        self.datafile = datafile
        self.x_offset = x_offset
        self.d_theta = 0.01
        self.save = save
        self.type = type
        self.coil_wire = coil_wiretype
        self.flux_file = flux_file
        self.wire_thickness = wire_thickness
        self.flux = None
        self.force = None
    def asym_flux_polar(self, R, b_z_r_vec):
        #computes the magnetic flux inside a circle with radius R, angular stepsize dtheta, offset a, in the x-direction from centre of the innercoil by integrating B_z(r) field
        b = np.load(self.datafile, allow_pickle=True)
        dr = b['radial_vectors'][1]   #stepsize of the radial vector
        if R>b['radial_vectors'][-1]:
            print('not possible')
            quit()
        n_theta = round(np.floor(np.pi/self.d_theta))  #no.of points in the theta coordinate
        int_vec = np.zeros(n_theta+1)  #initialize integral vector

        for i in range(0, n_theta+1):  #looping over all the angles (i*d_theta) less than pi
            #creating a B vector fiels and r vector field for a given angle theta
            b_vec_i = b_z_r_vec[b['radial_vectors']<((self.x_offset*np.cos(i*self.d_theta))+np.sqrt(R**2-(self.x_offset*np.sin(i*self.d_theta))**2))]
            r_vec_i = b['radial_vectors'][b['radial_vectors']<((self.x_offset*np.cos(i*self.d_theta))+np.sqrt(R**2-(self.x_offset*np.sin(i*self.d_theta))**2))]
            #integrating the Bfield in r-coordinate with differential rdr in polar
            int_vec[i] = np.trapz(r_vec_i*b_vec_i, dx=dr)
        self.flux = 2*np.trapz(int_vec, dx=self.d_theta)   #multiplying with 2 as the integral is only computed for positive y-axis
        return [self.flux]
    def asym_force(self, R, b_z_r_vec):
        # computes the magnetic flux inside a circle with radius R, angular stepsize dtheta, offset a, in the x-direction from centre of the innercoil by integrating B_z(r) field
        b = np.load(self.datafile, allow_pickle=True)
        dr = b['radial_vectors'][1]  # stepsize of the radial vector
        if R > b['radial_vectors'][-1]:
            print('not possible')
            quit()
        n_theta = round(np.floor(np.pi / self.d_theta))  # no.of points in the theta coordinate
        nor_for = np.zeros(n_theta + 1)
        for i in range(0, n_theta + 1):  # looping over all the angles (i*d_theta) less than pi
            # creating a B vector fiels and r vector field for a given angle theta
            b_vec_i = b_z_r_vec[b['radial_vectors'] < ((self.x_offset * np.cos(i * self.d_theta)) + np.sqrt(
                R ** 2 - (self.x_offset * np.sin(i * self.d_theta)) ** 2))]
            r_vec_i = b['radial_vectors'][b['radial_vectors'] < ((self.x_offset * np.cos(i * self.d_theta)) + np.sqrt(
                R ** 2 - (self.x_offset * np.sin(i * self.d_theta)) ** 2))]
            nor_for[i] = (2 * self.d_theta * np.pi * r_vec_i[i])*b_vec_i[i] / 360
        self.force = 2 * sum(nor_for)
        return [self.force]
    def outcoil(self, rad):
        #computes the flux phi(z) in Tm^2 by integrating the circle inside the outer coils at every z grid point with the outer coil offset 'a'
        b = np.load(self.datafile, allow_pickle=True)
        z_vec_len = len(b['z_vectors'])
        phi_vec = np.zeros(len(b['z_vectors']))

        for i in range(z_vec_len): #loop over all heights in z grid
            phi_vec[i] = self.asym_flux_polar(rad, b['mag_field_z'][i,:])[0]
        #creating the full phi_tot & z_tot vectors for the domain [-z_max,z_max] by mirroring the vectors in the domain [0, z_max]
        z_tot = np.concatenate((-np.flipud(b['z_vectors'][1:]), b['z_vectors'][1:]))
        phi_tot = np.concatenate((np.flipud(phi_vec[1:]), phi_vec[1:]))*(10**-6)  #converting from mm^2 to m^2
        if self.save:
            np.savez_compressed(self.flux_file, z_vec = z_tot, phi_vec = phi_tot)
        return [phi_tot, z_tot]
    def outcoil_for(self, rad):
        b = np.load(self.datafile, allow_pickle=True)
        z_vec_len = len(b['z_vectors'])
        phi_vec = np.zeros(len(b['z_vectors']))
        force_vec = np.zeros(len(b['z_vectors']))
        for i in range(z_vec_len): #loop over all heights in z grid
            force_vec[i] = self.asym_force(rad, b['mag_field_z'][i,:])[0]
        force_tot = np.concatenate((np.flipud(force_vec[1:]), force_vec[1:]))
        # if self.save:
        #     np.savez_compressed(self.flux_file, z_vec = z_tot, phi_vec = phi_tot)
        #return [z_tot, phi_tot]
        return [force_tot]
    def outcoil_flux(self, wire_thickness1, out_layers, out_radius, parallel_processing = None):
        #Total flux by looping over all outer coil layers and adding the flux of each layer
        phi_vec_list = []
        b = np.load(self.datafile, allow_pickle = True)
        for i in range(0, out_layers):
            rad_i = out_radius+(wire_thickness1*i)
            res_layer = self.outcoil(rad_i)
            phi_vec_list.append(res_layer[0])
            print('layer'+str(i+1) + ' : completed')
        z_vec_save = res_layer[1]
        if parallel_processing :
            processes = [Process(target=self.outcoil, args=(self.value[self.type]['out_rad']+(wire_thickness1*m))) for m in range(self.value[self.type]['out_layers'])]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            # for i in range(self.value[self.type]['out_layers']):
            #     z_vec, phi_vec =
        print('flux is in T.m^2')
        if self.save:
            np.savez_compressed(self.flux_file, z_vec = z_vec_save, phi_vec = sum(phi_vec_list),
                                Input_parameters = b['Input_parameters'], Coils_config = b['Coils_config'],
                                innercoil_voltage=b['innercoil_voltage'], innercoil_flux=b['innercoil_flux'],
                                upp_outercoil_voltage=b['upp_outercoil_voltage'], upp_outercoil_flux=b['upp_outercoil_flux'])
        return [z_vec_save, sum(phi_vec_list)]
    def outcoil_force(self, para1, wire_thickness1, out_layers, out_radius, parallel_processing = None):
        #Total flux by looping over all outer coil layers and adding the flux of each layer
        for_vec_list = []
        b = np.load(self.datafile, allow_pickle = True)
        for i in range(0, out_layers):
            rad_i = out_radius+(wire_thickness1*i)
            res_layer = self.outcoil_for(rad_i)
            for_vec_list.append(res_layer[0])
            print('layer : '+str(i+1) + 'completed')
        z_vec_save = res_layer[0]
        if parallel_processing :
            processes = [Process(target=self.outcoil, args=(self.value[self.type]['out_rad']+(wire_thickness1*m))) for m in range(self.value[self.type]['out_layers'])]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
        print('flux is in T.m^2')
        if self.save:
            np.savez_compressed(self.flux_file, z_vec = z_vec_save, for_vec = sum(for_vec_list),
                                Design_type = b['Design_type'], Input_parameters = b['Input_parameters'], Innercoil_config = b['Innercoil_config'],
                                innercoil_voltage=b['innercoil_voltage'], innercoil_flux=b['innercoil_flux'],
                                upp_outercoil_voltage=b['upp_outercoil_voltage'], upp_outercoil_flux=b['upp_outercoil_flux'])
        return [z_vec_save, sum(for_vec_list)]


class Voltages:
    #induced voltages for different z positions of the inner coil. Lower bdry of lower coil is -z_max, upper bdry of upper coil is z_max
    def __init__(self, loadfile):
        self.loadfile = loadfile
        #self.savefile = savefile
    def calculate(self, sim_range, outcoil_dist, outcoil_ht, out_wire_thickness, filename = None):
        b = np.load(self.loadfile)
        z_vec = b['z_vec'] ; phi_vec = b['phi_vec']
        print('len z_vec :', len(z_vec), z_vec[-1], z_vec[1])
        z_max = sim_range + (outcoil_ht + outcoil_dist) / 2
        if z_max>z_vec[-1]:
            print("z_max should be smaller than the z domain of the flux vector")
            sys.exit()
        z_lower = z_vec[0]  #lower bdry of the flux vector
        dz = z_vec[1] - z_vec[0] #stepsize of z vector

        z_n_min = round((-z_max-z_lower)/dz) #min n for bottom of lower coil
        z_n_max = round((z_max-z_lower -(outcoil_dist+outcoil_ht))/dz)  #max n for bottom of lower out coil


        print(z_n_min, z_n_max)
        v_induced_low = np.zeros(round(z_n_max-z_n_min)+1)
        v_induced_upp = v_induced_low   #initializing induced voltages for lower and upper coils

        #looping over all positions of outer coil & copute induced voltage in each coil by integrating phi(z) over the coil_ht.
        #introducing prefactor omega = 2*pi*f = 2*pi*10000
        for i in range(0, round(z_n_max-z_n_min)+1):
            v_induced_low[i] = np.sum(phi_vec[(z_n_min + round(out_wire_thickness / (2 * dz)) + i):
                                              (z_n_min + round((outcoil_ht - out_wire_thickness / 2) / dz) + i + 1):round(
                out_wire_thickness / dz)]) * 2 * np.pi * 10000
            v_induced_upp[i] = np.sum(phi_vec[(z_n_min + round((outcoil_dist + out_wire_thickness / 2) / dz) + i):(z_n_min
                + round((outcoil_dist + outcoil_ht - out_wire_thickness / 2) / dz) + i + 1):round(out_wire_thickness / dz)]) * 2 * np.pi * 10000
        # chainging the new z positions for centre of inner coil into dz step of 0.1
        z_vec_new = z_vec[z_n_min:z_n_max + 1] + (outcoil_dist + outcoil_ht) / 2
        print('no of windings computed')
        if filename:
            np.savez_compressed(filename, z_vec = z_vec_new, v_low = v_induced_low, v_upp = v_induced_upp,
                                v_upp_corrected = np.flipud(v_induced_upp))
        return [z_vec_new, v_induced_low, v_induced_upp, np.flipud(v_induced_upp)]

class Plots:
    def __init__(self, filename):
        self.filename = filename
        self.b = np.load(self.filename, allow_pickle=True)
    def bfield_plot(self, parameter, shift_z = 0, n_quiver_r=None, n_quiver_z=None):
        r_vec = self.b['radial_vectors'];z_vec= self.b['z_vectors']
        mag_field_z  = self.b['mag_field_z'];mag_field_r= self.b['mag_field_r']
        z_tot = np.concatenate((-np.flipud(z_vec[1:]), z_vec))
        b_z_tot = np.concatenate((np.flipud(mag_field_z[1:, :]), mag_field_z), axis=0)
        b_r_tot = np.concatenate((-np.flipud(mag_field_r[1:, :]), mag_field_r), axis=0)
        r_v, z_v = np.meshgrid(r_vec, z_tot)
        b_tot = np.sqrt(b_r_tot**2 + b_z_tot**2)
        dz = z_tot[1] - z_tot[0]; dr = r_vec[1] - r_vec[0]

        if parameter == 'contour_norm':
            fig1, ax1 = plt.subplots(layout = 'constrained')
            cs = ax1.contourf(r_v, z_v, b_tot/np.amax(b_tot), cmap = 'jet')
            cbar = fig1.colorbar(cs)
            cbar.ax.set_ylabel(r'$B/B_{max}$')
            contourplot = False
        if parameter == 'contourplot':
            'Scaling of colorbar is not correct yet'
            fig1, ax1 = plt.subplots(layout='constrained')
            CS = ax1.contourf(r_v, z_v, b_tot, cmap='jet')
            cbar = fig1.colorbar(CS)
            cbar.ax.set_ylabel('|B| [T]')
        if parameter == 'quiverplot':
            rows = np.arange(0, len(z_tot), n_quiver_z)
            cols = np.arange(0, len(r_vec), n_quiver_r)
            # normalize all vectors for a clearer plot
            b_mat_r_norm = b_r_tot / b_tot
            b_mat_z_norm = b_z_tot / b_tot
            plt.quiver(r_v[rows, :][:, cols], z_v[rows, :][:, cols], b_mat_r_norm[rows, :][:, cols],
                       b_mat_z_norm[rows, :][:, cols], cmap='plasma')
        if parameter == 'coil':
            input_parameters1 = self.b['Input_parameters'].item()
            input_parameters = self.b['Innercoil_config'].item()
            out_dist = input_parameters['out_dist']
            out_ht = input_parameters['out_ht']
            wire_width, wire_ins = input_parameters1['outercoil Diameter(mm)_Insulation(mm)_Wiretype'][0:2]
            wire_tot = wire_width + 2 * wire_ins
            # plot the emitting coil as a rectangle
            plt.gca().add_patch(
                (Rectangle((input_parameters['inn_rad'], (input_parameters['inn_dist'] - input_parameters['inn_ht']) / 2), wire_tot * input_parameters['inn_layers']
                           , input_parameters['inn_ht'], edgecolor='blue', facecolor='none', lw=2)))
            # plot the receiving coils as rectangles
            plt.gca().add_patch((Rectangle((input_parameters['out_rad'], 0.5 * (input_parameters['out_dist'] - input_parameters["out_ht"]) + shift_z),
                                           wire_tot * input_parameters['out_layers'], input_parameters["out_ht"], edgecolor='red',
                                           facecolor='none', lw=2)))
            plt.gca().add_patch((Rectangle((input_parameters['out_rad'], -0.5 * (input_parameters['out_dist'] + input_parameters['out_ht']) + shift_z),
                                           wire_tot * input_parameters['out_layers'], input_parameters['out_ht'], edgecolor='red',
                                           facecolor='none', lw=2)))





