from materials import feed as feed

class Sensortype:
    def __init__(self, InnCoilCurrent, Simfreq, OutCoilCurrent):
        """
        class to determine the type of sensor.
        In general, 20mA-10khZ Inner coil current with no outer coil current indicates LVDT. 1A DC outer coil current with no inner coil current indicates VC
        ________INPUT________
        InnCoilCurrent: Inner coil current in Amps_(float)
        Simfreq: Frequency in Hz_(float)
        OutCoilCurrent: Outer coil current in Amps_(float)
        """
        self.InnCoilCurrent = InnCoilCurrent; self.OutCoilCurrent = OutCoilCurrent
        self.Simfreq = Simfreq

    def para(self):
        """
        method in the class 'Sensortype' that returns the list containing inner coil current(in Amps), excitation frequency(in Hz), outer coil current(in Amps)
        returns a list containing sensor parameters
        _______Output_______
        [Inner coil current, Frequency, Outer coil current]
        """
        return [self.InnCoilCurrent, self.Simfreq, self.OutCoilCurrent]

class Simulation:
    def __init__(self, Nsteps, stepsize, inncoil_offset, data_file, fit_points = None):
        """
        class to determine the coil motion/Pre-simulation parameters
        ________INPUT________
        Nsteps: Total no. of inner coil steps_(int)
        stepsize: step/grid width_(float)
        Inner coil offset: Initial inner coil offset_(float)
        data_file : name of the file_(string)
        """
        self.Nsteps = Nsteps; self.stepsize = stepsize; self.fit_points = fit_points
        self.inncoil_offset = inncoil_offset; self.data_file = data_file

    def parameters(self):
        """
            method in the class 'Simulation' returns the coil motion parameters
            _______Output_______
            [Nsteps, stepsize, inncoil_offset, data_file, fit_points]
        """
        return [self.Nsteps, self.stepsize, self.inncoil_offset, self.data_file, self.fit_points]
class Wiretype:
    def __init__(self, outcoil_material=None, inncoil_material=None, magnet_material = None):
        """
            class to determine the coil materials
            ________INPUT________
            Outer coil_material: Name of the outer coil material_(string)
            Inner coil_material: Name of the inner coil material_(string)
            Magnet_material: Name of the imagnet material_(string)
         """
        self.outcoil_material = outcoil_material
        self.inncoil_material = inncoil_material
        self.magnet_material = magnet_material
        self.wire_feed = feed.wire_types
        self.magnet_feed = feed.magnet_types

    def prop_out(self):
        """
            method in the class 'Wiretype' that returns the outer coil wire properties
            _______Output_______
            [wire_dia, insulation_thickness, wire_type, resistance(Ω/mm), electrical_conductivity, resistivity(Ω*m), magnetic_perm(H/m)]
        """
        return self.wire_feed[self.outcoil_material]
    def prop_inn(self):
        """
            method in the class 'Wiretype' that returns the inner coil wire properties
            _______Output_______
            [wire_dia, insulation_thickness, wire_type, resistance(Ω/mm), electrical_conductivity, resistivity(Ω*m), magnetic_perm(H/m)]
        """
        return self.wire_feed[self.inncoil_material]
    def mag_mat(self):
        """
            method in the class 'Wiretype' that returns the magnet properties
            _______Output_______
            [magnet_type]
        """
        return self.magnet_material

    def yoke_mat(self):
        mate = "Pure iron, annealed"
        return mate

class Geometry:
    def __init__(self, inn_ht, inn_rad, inn_layers, inn_dist, out_ht=None, out_rad=None, out_layers=None, out_dist=None, mag_len=None, mag_dia=None, ver_shi=None,
                 innlow_ht = None,innlow_rad = None,innlow_layers = None, mag_ht=None, mag_innrad=None, mag_outrad=None, mag_ver_shi=None):
        """
            class to determine the coil geometry
            ________INPUT________
            inn_ht: Inner coil height_(float)
            inn_rad: Inner coil radius_(float)
            inn_layers = Inner coil layers_(float)
            inn_dist = Inner coil distance_(float)
            out_ht = Outer coil height_(float)
            out_rad = Outer coil radius_(float)
            out_layers = Outer coil layers_(float)
            out_dist = Outer coil distance_(float)
            mag_len = Magnet length_(float)
            mag_dia = Magnet diameter_(float)
            ver_shi = Vertical shift_(float)
         """
        self.inn_ht = inn_ht; self.inn_rad = inn_rad; self.inn_layers = inn_layers
        self.inn_dist = inn_dist; self.out_dist = out_dist
        self.out_ht = out_ht; self.out_rad = out_rad; self.out_layers = out_layers
        self.mag_len = mag_len; self.mag_dia = mag_dia; self.ver_shi = ver_shi
        self.innLOW_ht = innlow_ht; self.innLOW_rad = innlow_rad; self.innLOW_layers = innlow_layers
        self.mag_ht = mag_ht; self.mag_innrad = mag_innrad; self.mag_outrad = mag_outrad; self.mag_ver_shi = mag_ver_shi

    def inncoil(self):
        """
            method in the class 'Geometry' that returns the geometric properties of the inner coil
            _______Output_______
            [ inner coil height, inner coil radius, no. of layers, distance between coils]
        """
        return [self.inn_ht, self.inn_rad, self.inn_layers, self.inn_dist]
    def Low_Inncoil(self):
        """
            method in the class 'Geometry_yoke' that returns the geometric properties of the lower inner coil
            _______Output_______
            [ lower inner coil height, lower inner coil radius, no. of layers, distance between coils]
        """
        return [self.innLOW_ht, self.innLOW_rad, self.innLOW_layers, self.inn_dist]
    def outcoil(self):
        """
            method in the class 'Geometry' that returns the geometric properties of the outer coil
            _______Output_______
            [ outer coil height, outer coil radius, no. of layers, distance between outer coils]
        """
        return [self.out_ht, self.out_rad, self.out_layers, self.out_dist]
    def mag(self):
        """
            method in the class 'Geometry' that returns the geometric properties of the magnet
            _______Output_______
            [ magnet height, magnet diameter, magnet shift]
        """
        return [self.mag_len, self.mag_dia, self.ver_shi]
    def mag_yoke(self):
        """
            method in the class 'Geometry_yoke' that returns the geometric properties of the magnet
            _______Output_______
            [ magnet height, magnet radius, magnet shift]
        """
        mag_rad = self.mag_outrad - self.mag_innrad
        return [self.mag_ht, mag_rad, self.mag_ver_shi]

class Dimensions:
    def __init__(self, input_dimensions, variable):
        self.in_dim = input_dimensions; self.def_var = variable
        for key, value in self.in_dim.items():
            if any(not isinstance(num, (int, float)) for num in value):
                self.in_dim[key] = [self.def_var if not isinstance(num, (int, float)) else num for num in value]
    def inner_coil(self):
        return self.in_dim['inner']
    def outer_coil(self):
        return self.in_dim['outer']
    def magnet(self):
        return self.in_dim['magnet']

class Blocks:
    def __init__(self, lvdt_type):
        self.type = lvdt_type
        self.yoke_dim = feed.blocks

    def dimension(self, block:str):
        #length, height
        return [self.yoke_dim[self.type][block][0], self.yoke_dim[self.type][block][1]]


