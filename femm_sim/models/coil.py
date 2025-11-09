import numpy as np
from materials import feed as feed

class Position():
    """
    Modelling of the coils considering all the geometric parameters, for instance, radius, height etc.
    """
    def __init__(self, inn_ht=None, inn_rad=None, inn_layers=None, inn_dist=None, out_ht=None, out_rad=None, out_layers=None,  out_dist=None,
                 ver_shi=None, inn_wiredia=None, inn_wireins=None, out_wiredia=None, out_wireins=None, mag_len=None, mag_dia=None):
        self.inn_ht = inn_ht; self.inn_rad = inn_rad; self.inn_layers = inn_layers; self.inn_dist = inn_dist
        self.out_ht = out_ht; self.out_rad = out_rad; self.out_layers = out_layers; self.out_dist = out_dist
        self.inn_wiredia = inn_wiredia; self.out_wiredia = out_wiredia
        self.inn_wireins = inn_wireins; self.out_wireins = out_wireins
        self.mag_len = mag_len; self.mag_dia = mag_dia; self.ver_shi = ver_shi

        # Geometric consistency checks
        if any(param < 0 for param in [inn_ht, inn_rad, inn_layers, inn_dist, out_ht, out_rad, out_layers, out_dist,
                                           inn_wiredia, inn_wireins, out_wiredia, out_wireins, mag_len, mag_dia, ver_shi]):
            raise ValueError("All geometric parameters must be positive.")

        if inn_rad is not None and out_rad is not None and inn_rad > out_rad:
            raise ValueError("Inner coil radius must be smaller than (or equal to) outer coil radius (inn_rad < out_rad).")

        if out_dist is not None and out_ht is not None and out_dist <= out_ht:
            raise ValueError("Outer coil distance (from coil centres) must be greater than its height (out_dist > out_ht).")

        if mag_dia is not None and mag_dia > 2*out_rad:
            raise ValueError("Magnet diameter must be less than the coil diameter")

    def inncoil(self):
        """
        returns the modelled inner coil co-ordinates and wound layers
        _________output__________
        [InnCoil_OutRadius, InnCoil_Lowend, InnCoil_Uppend, InnCoil_NrWind_p_Layer, InnCoil_NrWindings,
                InnCoil_Circuit_name]
        """
        InnCoil_OutRadius = self.inn_rad + ((self.inn_wiredia + self.inn_wireins * 2) * self.inn_layers)
        #InnCoil_Lowend = (self.inn_dist - self.inn_ht) / 2
        InnCoil_Lowend = (0 - self.inn_ht) / 2
        InnCoil_Uppend = InnCoil_Lowend + self.inn_ht
        InnCoil_NrWind_p_Layer = (self.inn_ht) / (self.inn_wiredia + self.inn_wireins * 2)
        InnCoil_NrWindings = InnCoil_NrWind_p_Layer * self.inn_layers
        InnCoil_Circuit = "InnCoil_Circuit"
        return [InnCoil_OutRadius, InnCoil_Lowend, InnCoil_Uppend, InnCoil_NrWind_p_Layer, InnCoil_NrWindings,
                InnCoil_Circuit]
        
    def upp_outcoil(self):
        """
            returns the modelled upper outer coil co-ordinates and wound layers
            _________output__________
            [UppOutCoil_OutRadius, UppOutCoil_LowEnd, UppOutCoil_UppEnd, UppOutCoil_NrWind_p_Layer,
                UppOutCoil_NrWindings, UppOutCoil_Circuit]
        """
        UppOutCoil_OutRadius = self.out_rad + (
                    (self.out_wiredia + self.out_wireins * 2) * self.out_layers)
        UppOutCoil_LowEnd = (self.out_dist - self.out_ht) / 2
        UppOutCoil_UppEnd = UppOutCoil_LowEnd + self.out_ht
        UppOutCoil_NrWind_p_Layer = (self.out_ht) / (self.out_wiredia + self.out_wireins * 2)
        UppOutCoil_NrWindings = UppOutCoil_NrWind_p_Layer * self.out_layers
        UppOutCoil_Circuit = "UppOutCoil_Circuit"
        return [UppOutCoil_OutRadius, UppOutCoil_LowEnd, UppOutCoil_UppEnd, UppOutCoil_NrWind_p_Layer,
                UppOutCoil_NrWindings, UppOutCoil_Circuit]
        
    def low_outcoil(self):
        """
            returns the modelled lower outer coil co-ordinates and wound layers
            _________output__________
            [LowOutCoil_OutRadius, LowOutCoil_UppEnd, LowOutCoil_LowEnd, LowOutCoil_NrWind_p_Layer,
                LowOutCoil_NrWindings, LowOutCoil_Circuit]
        """
        LowOutCoil_OutRadius = self.out_rad + (
                    (self.out_wiredia + self.out_wireins * 2) * self.out_layers)
        LowOutCoil_UppEnd = -1 * (self.out_dist - self.out_ht) / 2
        LowOutCoil_LowEnd = LowOutCoil_UppEnd - self.out_ht
        LowOutCoil_NrWind_p_Layer = (LowOutCoil_UppEnd - LowOutCoil_LowEnd) / (
                    self.out_wiredia + self.out_wireins * 2)
        LowOutCoil_NrWindings = LowOutCoil_NrWind_p_Layer * self.out_layers
        LowOutCoil_Circuit = "LowOutCoil_Circuit"
        return [LowOutCoil_OutRadius, LowOutCoil_LowEnd, LowOutCoil_UppEnd, LowOutCoil_NrWind_p_Layer,
                LowOutCoil_NrWindings, LowOutCoil_Circuit]

    def magnet(self):
        """
            returns the modelled magnet co-ordinates
            _________output__________
            [Magnet_UppEnd, Magnet_LowEnd, Magnet_Radius]
        """
        Magnet_UppEnd = self.mag_len / 2 + self.ver_shi
        Magnet_LowEnd = -self.mag_len / 2 + self.ver_shi
        Magnet_Radius = self.mag_dia / 2
        return [Magnet_UppEnd, Magnet_LowEnd, Magnet_Radius]
    
class Length:
    """
    Calculates the total length of the coil wire
    """
    def __init__(self, inn_layers=None, inn_rad=None, inn_wiredia=None, inn_wireins=None, innwind_pr_layer=None, out_layers=None,
                 out_rad=None, out_wiredia=None, out_wireins=None, outwind_pr_layer=None):
        self.inn_layers = inn_layers; self.inn_rad = inn_rad; self.inn_wiredia = inn_wiredia
        self.inn_wireins = inn_wireins; self.innwind_pr_layer = innwind_pr_layer
        self.out_layers = out_layers; self.out_rad = out_rad
        self.out_wiredia = out_wiredia; self.out_wireins = out_wireins; self.outwind_pr_layer = outwind_pr_layer

    def inncoil(self):
        """
        returns the total length of the inner coil wire
        _________output__________
            Inner coil wire length
        """
        InnCoil_TotalWire = 0
        inn_wire_thickness = self.inn_wiredia + (self.inn_wireins * 2)
        for i in range(0, int(self.inn_layers)):
            circ = 2 * np.pi * (self.inn_rad + (i * inn_wire_thickness))
            InnCoil_TotalWire += circ * self.innwind_pr_layer
        extra_layer = 2 * np.pi * (self.inn_rad + (i+1) * (self.inn_wiredia + self.inn_wireins * 2))
        extra_circ = extra_layer*(self.inn_layers-int(self.inn_layers))
        return InnCoil_TotalWire+extra_circ

    def upp_outcoil(self):
        """
        returns the total length of the upper outer coil wire
        _________output__________
            Upper outer coil wire length
        """
        UppOutCoil_TotalWire = 0
        out_wire_thickness = self.out_wiredia + (self.out_wireins * 2)
        for i in range(0, int(self.out_layers)):
            circ = 2 * np.pi * (self.out_rad + (i * out_wire_thickness))
            UppOutCoil_TotalWire += circ * self.outwind_pr_layer
        extra_layer = 2 * np.pi * (self.out_rad + (i + 1) * (self.out_wiredia + self.out_wireins * 2))
        extra_circ = extra_layer * (self.out_layers - int(self.out_layers))
        return UppOutCoil_TotalWire+extra_circ

    def low_outcoil(self):
        """
        returns the total length of the lower outer coil wire
        _________output__________
            lower outer coil wire length
        """
        LowOutCoil_TotalWire = 0
        out_wire_thickness = self.out_wiredia + (self.out_wireins * 2)
        for i in range(0, int(self.out_layers)):
            # circ = 2*np.pi*LowOutCoil_InRadius+i*(LowOutCoil_WireDiam+LowOutCoil_WireInsul)
            circ = 2 * np.pi * (self.out_rad + (i * out_wire_thickness))
            LowOutCoil_TotalWire += circ * self.outwind_pr_layer
        extra_layer = 2 * np.pi * (self.out_rad + (i + 1) * (self.out_wiredia + self.out_wireins * 2))
        extra_circ = extra_layer * (self.out_layers - int(self.out_layers))
        # print("Total length of lower out coil wire (mm):", LowOutCoil_TotalWire, ' and extra :', extra_circ)
        return LowOutCoil_TotalWire+extra_circ

class Coil_prop:
    """
    properties of the coils such as currents, voltages, fluxes, acted forces e.t.c
    """
    def __init__(self, steps):
        self.steps = steps
    def gen_coil(self):
        currents = np.zeros(self.steps + 1).astype(complex)
        voltages = np.zeros(self.steps + 1).astype(complex)
        flux = np.zeros(self.steps + 1).astype(complex)
        forces = np.zeros(self.steps + 1).astype(complex)
        positions = np.zeros(self.steps + 1).astype(complex)
        return {'current': currents, 'voltage': voltages, 'flux': flux, 'force': forces, 'position': positions}
    def magnet(self):
        """
            returns the modelled magnet properties
            _________output__________
            [Magnet force]
        """
        magnet_forces = np.zeros(self.steps+1)
        return {'Magnet_forces':magnet_forces}