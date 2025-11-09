from sensors import LVDT as LVDT
from sensors import VC as VC
from sensors import LVDT_com as LVDT_com
from sensors import VC_only as VC_only
from sensors import YOKE as YOKE
from sensors import VC_fields as VC_fields
from simulation import LVDT_correction as LVDT_correction
from simulation import LVDT_mutual_inductance as LVDT_mutual_inductance

class Position_sensor:
    """
    Class for simulating position sensors within specified ranges.

    Parameters:
    ----------
    sensor_type : str
        Type of the position sensor to be simulated.

    save : bool
        Whether to save the simulated data or not.

    sim_range : list
        Required simulation range. A list of length 3 containing:
        1. Total simulation points
        2. Step size
        3. Offset/lower limit of the moving coil.

    data : str
        Name of the file, whether the simulating design is default NIKHEF design or not,
        and type/parameter of the design.

    mat_prop : list, optional
        List of materials used (inner coil material, outer coil material, magnet material) in simulation.
        Default is ['32 AWG', '32 AWG', 'N40'].

    boundary conditions : list, optional
        list with boundary conditions for airspace-1, airspace-2, material of boundary and label.
        Default is [150, 300, 'Air', 'Outside'].

    lvdt_dim : dict, optional
        dictionary specifying coil geometry in simulation.
        The keys of this dictionary are 'inner', 'outer', 'magnet'.
        The values of these keys are lists containing the values(in mm) of height, radius, layers, distance (in the order) for the coils and length, diameter (in the order) for the magnet.

    simulation : str, optional
        Type of the simulation.
        Default is 'femm'.

    """
    def __init__(self, sensor_type, save, sim_range, data=None, material_prop=None, dimensions=None, simulation=None, boundary=None):
        self.sensor_type = sensor_type
        self.save = save
        self.data = data
        self.lvdt_dim = dimensions
        self.material_prop = material_prop if material_prop is not None else ['32 AWG', '32 AWG', 'N40']
        self.simulation_type = [simulation]*len(sensor_type)
        self.sim_range = sim_range
        self.boundary = boundary if boundary is not None else [150, 'Air', 0.5,  300, 'Air', 1, 'Outside']
        self.simulation_range = self.sim_range['steps_size_offset'] if self.simulation_type != 'semi_analytical' else {'setps_size_offset':[[1,1,0]]}
    def execute(self, input_current = None):
        """
        Executes the simulation with above defined parameters
        Parameters:
        ----------
        input_current : list, optional
            Inner coil current(in Amp), frequency(in Hz), outer coil(upper and lower currents in a tuple) for the simulation. Default values for LVDT is [0.02, 10000, [0,0]] and for VC is [0, 0, [1,1]]
        """
        for i in range(len(self.sensor_type)):
            if self.sensor_type[i] == 'LVDT':
                excitation = input_current if input_current is not None else [0.02, 10000, [0, 0]]
                if self.data['is default'][i] == 'yes':
                    a = LVDT.Analysis(self.save, sim_range=self.simulation_range[i],
                                      default=self.data['is default'][i], filename=self.data['filename(s)'][i], input_excitation=excitation, design_type=self.data['design or parameter'][i],
                                      materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], simulation_type=self.simulation_type[i], boundary_conditions=self.boundary)
                    meta_data = a.simulate()
                else:
                    a = LVDT.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                      default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, design_type=None, coil_dimensions=self.lvdt_dim, boundary_conditions=self.boundary,
                                      materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], parameter1=None, simulation_type=self.simulation_type[i])
                    meta_data = a.simulate()
            if self.sensor_type[i] == 'VC':
                excitation = input_current if input_current is not None else [0, 0, [1, 1]]
                if self.data['is default'][i] == 'yes':

                    a = VC.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                    default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, boundary_conditions=self.boundary,
                                    design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], simulation_type=self.simulation_type[i])
                    meta_data = a.simulate()
                else:
                    a = VC.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i], boundary_conditions=self.boundary,
                                    default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, design_type=None, coil_dimensions=self.lvdt_dim,
                                    materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], parameter1=None, simulation_type=self.simulation_type[i])
                    meta_data = a.simulate()
            if self.sensor_type[i] == 'VC_only':
                excitation = input_current if input_current is not None else [0, 0, [1]]
                if self.data['is default'][i] == 'yes':
                    a = VC_only.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                         default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, boundary_conditions=self.boundary,
                                         design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1]])
                    meta_data = a.simulate()
                else:
                    a = VC_only.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                         default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation,design_type=None, coil_dimensions=self.lvdt_dim,
                                         parameter1=None, materials =[self.material_prop[0], self.material_prop[1]], boundary_conditions=self.boundary)
                    meta_data = a.simulate()
            if self.sensor_type[i] == 'LVDT with yoke':
                excitation = input_current if input_current is not None else [1, 0, [0]]
                if self.data['is default'][i] == 'yes':
                    a = YOKE.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                      default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, boundary_conditions=self.boundary,
                                      design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]])
                    meta_data = a.simulate()
                else:
                    a = YOKE.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                      default=self.data['is default'][i], filename=self.data['filename(s)'][i],
                                      design_type=None, parameter1=None)
                    meta_data = a.simulate()
            if self.sensor_type[i] == 'VC_fields':
                excitation = input_current if input_current is not None else [0, 0, [1, 1]]
                print('vc_analytical')
                if self.data['is default'][i] == 'yes':
                    a = VC_fields.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i], input_excitation=excitation, boundary_conditions=self.boundary,
                                           default=self.data['is default'][i], filename=self.data['filename(s)'][i],
                                           design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]])
                    meta_data = a.simulate()
                else:
                    a = VC_fields.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                           default=self.data['is default'][i], filename=self.data['filename(s)'][i], input_excitation=excitation, boundary_conditions=self.boundary, coil_dimensions=self.lvdt_dim,
                                           design_type=None, materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], parameter1=None)
                    meta_data = a.simulate()
            if self.sensor_type[i] == 'LVDT_corrected':
                excitation = input_current if input_current is not None else [0.02, 10000, 0]
                if self.data['is default'][i] == 'yes':
                    a1 = LVDT_correction.Analysis(save = self.save, default=self.data['is default'][i], offset=self.sim_range['steps_size_offset'][i],input_excitation=excitation,
                                       design=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], filename=self.data['filename(s)'][i])
                    meta_data = a1.simulate()
                else:
                    a1 = LVDT_correction.Analysis(save = self.save, default=self.data['is default'][i], offset=self.sim_range['steps_size_offset'][i],input_excitation=excitation, design=None, coil_dimensions=self.lvdt_dim,
                                        materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]],  filename=self.data['filename(s)'][i], parameter=self.data['design or parameter'][i])
                    meta_data = a1.simulate()
            if self.sensor_type[i] == 'LVDT_mutual_inductance':
                excitation = input_current if input_current is not None else [0.02, 10000, 0]
                if self.data['is default'][i] == 'yes':
                    a1 = LVDT_mutual_inductance.Analysis1(save = self.save, default=self.data['is default'][i], offset=self.sim_range['steps_size_offset'][i],
                                       design_type=self.data['design or parameter'][i], input_excitation=excitation, materials1 =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], filename1=self.data['filename(s)'][i])
                    meta_data = a1.simulate()
                else:
                    a1 = LVDT_mutual_inductance.Analysis1(save = self.save, default=self.data['is default'][i], offset=self.sim_range['steps_size_offset'][i],coil_dimensions1=self.lvdt_dim,
                                        design_type=None,input_excitation=excitation, materials1 =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], filename1=self.data['filename(s)'][i], parameter1=self.data['design or parameter'][i])
                    meta_data = a1.simulate()
            if self.sensor_type[i] == 'LVDT_com':
                excitation = input_current if input_current is not None else [0.02, 10000, [0, 0]]
                if self.data['is default'][i] == 'yes':

                    a = LVDT_com.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
                                    default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, boundary_conditions=self.boundary,
                                    design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], simulation_type=self.simulation_type[i])
                    meta_data = a.simulate()
                else:
                    a = LVDT_com.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i], boundary_conditions=self.boundary,
                                    default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation, design_type=None, coil_dimensions=self.lvdt_dim,
                                    materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], parameter1=None, simulation_type=self.simulation_type[i])
                    meta_data = a.simulate()
            # if self.sensor_type[i] == 'inner_coil':
            #     excitation = input_current if input_current is not None else [0, 0, [1, 1]]
            #     print('single_coil')
            #     if self.data['is default'][i] == 'yes':
            #         a = single_coil_fields.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],input_excitation=excitation,
            #                           default=self.data['is default'][i], filename=self.data['filename(s)'][i],
            #                           design_type=self.data['design or parameter'][i], materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]])
            #         a.simulate()
            #     else:
            #         a = single_coil_fields.Analysis(self.save, sim_range=self.sim_range['steps_size_offset'][i],
            #                           default=self.data['is default'][i], filename=self.data['filename(s)'][i],input_excitation=excitation,
            #                           design_type=None,materials =[self.material_prop[0], self.material_prop[1], self.material_prop[2]], parameter1=self.data['design or parameter'][i])
            #         a.simulate()


        return meta_data
            




