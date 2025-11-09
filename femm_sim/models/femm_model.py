import femm
from materials import feed as feed

wires = feed.wire_types
magnets = feed.magnet_types
class Femm_bc():
    """
        Class to define and create boundary conditions for the FEMM model.
    """
    def __init__(self, AirSpaceRadius_1, material1:str, grid1, AirSpaceRadius_2, material2:str, grid2, BC_Name, BC_Group, parameter=None):
        """
        Initialize the boundary conditions for the FEMM model.

        Parameters
        ----------
        AirSpaceRadius_1 : float
            Radius of the selected space 1.
        AirSpaceRadius_2 : float
            Radius of the selected space 2.
        BC_Name : str
            Name of the boundary region.
        BC_Group : int
            Group number of the region.
        material : str
            Material of the boundary region (e.g., vacuum, air). Should be chosen from the material library in FEMM or should be defined separately.
        parameter : optional
            Additional parameter for the boundary condition.

        Returns
        -------
        None
        """
        self.AirSpaceRadius_1 = AirSpaceRadius_1; self.AirSpaceRadius_2 = AirSpaceRadius_2
        self.BC_Name = BC_Name; self.BC_Group = BC_Group
        self.material1 = material1; self.material2 = material2; self.grid1 = grid1; self.grid2 = grid2
        self.parameter = parameter
        # Airspace1
        femm.mi_drawline(0, self.AirSpaceRadius_1, 0, -self.AirSpaceRadius_1)
        femm.mi_drawarc(0, -self.AirSpaceRadius_1, 0, self.AirSpaceRadius_1, 180, 2)
        femm.mi_getmaterial(self.material1)
        femm.mi_clearselected()
        femm.mi_addblocklabel(self.AirSpaceRadius_1 / 4, self.AirSpaceRadius_1 / 2)
        femm.mi_selectlabel(self.AirSpaceRadius_1 / 4, self.AirSpaceRadius_1 / 2)
        femm.mi_setblockprop(self.material1, 0, self.grid1, '', 0, 0, 0)
        #femm.mi_setblockprop("Air", 1, 0, '', 0, 0, 0)
        femm.mi_clearselected()
        # Airspace2
        femm.mi_drawline(0, self.AirSpaceRadius_2, 0, -self.AirSpaceRadius_2)
        femm.mi_drawarc(0, -self.AirSpaceRadius_2, 0, self.AirSpaceRadius_2, 180, 2)
        femm.mi_getmaterial(self.material2)
        femm.mi_clearselected()
        femm.mi_addblocklabel(self.AirSpaceRadius_2 / 2, self.AirSpaceRadius_2 / 1.2)
        femm.mi_selectlabel(self.AirSpaceRadius_2 / 2, self.AirSpaceRadius_2 / 1.2)
        #femm.mi_setblockprop(self.material2, 1, 0, '', 0, 0, 0)
        femm.mi_setblockprop(self.material2, 0, self.grid2, '', 0, 0, 0)
        femm.mi_clearselected()
        # Boundary properties
        femm.mi_addboundprop(self.BC_Name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        femm.mi_clearselected()
        femm.mi_selectarcsegment(0, self.AirSpaceRadius_2)
        #femm.mi_selectarcsegment(0, self.AirSpaceRadius_1)
        femm.mi_setarcsegmentprop(2, self.BC_Name, 0, self.BC_Group)
        femm.mi_clearselected()

class Femm_coil():
        """
        Class to define and create a (circular) coil with a defined current.
        """
        def __init__(self, x1, y1, x2, y2, circ_name, circ_current, circ_type, material, edit_mode, group, label1, label2, blockname, turns_pr_layer
                     , parameter=None,simulation_type=None):
            """
            Initialize the coil with the specified properties and current.

            Parameters
            ----------
            x1 : float
                x-coordinate of the edge of the rectangle (planar view of the circular coil is a rectangle).
            y1 : float
                y-coordinate of the edge of the rectangle (planar view of the circular coil is a rectangle).
            x2 : float
                x-coordinate of the diagonally opposite edge of (x1, y1) on the rectangle.
            y2 : float
                y-coordinate of the diagonally opposite edge of (x1, y1) on the rectangle.
            circ_name : str
                Name of the circuit.
            circ_current : float
                Current in the circuit.
            circ_type : int
                Type of connection (0 for parallel, 1 for series).
            material : str
                Material of the coil/wire chosen from the FEMM library.
            edit_mode : int
                Entities in the model block that can be edited when the block is selected (0-nodes, 1-block labels, 2-segments, 3-arcs, 4-all entity types).
            group : int
                Group of the coil.
            label1 : float
                x-coordinate of block label location.
            label2 : float
                y-coordinate of block label location.
            blockname : str
                Name of the block.
            turns_pr_layer : float
                Number of turns per layer.
            parameter : optional
                Additional parameter for the coil.
            simulation_type : optional
                Type of simulation (e.g., 'semi_analytical').

            Returns
            -------
            None

            Example
            -------

            """
            self.x1 = x1; self.y1 = y1
            self.x2 = x2; self.y2 = y2
            self.circ_name = circ_name; self.circ_current = circ_current
            self.circ_type = circ_type; self.material = material
            self.edit_mode = edit_mode; self.group = group
            self.label1 = label1; self.label2 = label2
            self.blockname = blockname
            self.turns_pr_layer = turns_pr_layer
            self.parameter = parameter
            self.simulation_type = simulation_type
            femm.mi_drawrectangle(self.x1, self.y1, self.x2, self.y2)
            femm.mi_addcircprop(self.circ_name, self.circ_current, self.circ_type)
            try:
                femm.mi_getmaterial(self.material)
            except:
                femm.mi_addmaterial(wires[self.material][2], 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, wires[self.material][0])

            femm.mi_clearselected()
            femm.mi_selectrectangle(self.x1, self.y1, self.x2, self.y2, self.edit_mode)
            femm.mi_setgroup(self.group)
            femm.mi_clearselected()
            femm.mi_addblocklabel(self.x1+self.label1, self.y2+(self.label2/2))
            femm.mi_selectlabel(self.x1+self.label1, self.y2+(self.label2/2))
            if self.simulation_type=='semi_analytical':
                femm.mi_setblockprop(self.blockname, 0, 0.005, self.circ_name, 0, self.group, self.turns_pr_layer)
            else:
                femm.mi_setblockprop(self.blockname, 1, 0, self.circ_name, 0, self.group, self.turns_pr_layer)
            femm.mi_clearselected()

class Femm_magnet():
        """
        Class to define and create a magnet.
        """
        def __init__(self, x1, y1, x2, y2, material, edit_mode, group, label1, label2):
            """
        Initialize the magnet with the specified properties.

        Parameters
        ----------
        x1 : float
            x-coordinate of the edge of the rectangle (planar view of the cylindrical magnet is a rectangle).
        y1 : float
            y-coordinate of the edge of the rectangle (planar view of the cylindrical magnet is a rectangle).
        x2 : float
            x-coordinate of the diagonally opposite edge of (x1, y1) on the rectangle.
        y2 : float
            y-coordinate of the diagonally opposite edge of (x1, y1) on the rectangle.
        material : str
            Material of the magnet chosen from the FEMM library.
        edit_mode : int
            Entities in the model block that can be edited when the block is selected (0-nodes, 1-block labels, 2-segments, 3-arcs, 4-all entity types).
        group : int
            Group of the magnet.
        label1 : float
            x-coordinate of block label location.
        label2 : float
            y-coordinate of block label location.

        Returns
        -------
        None

        Example
        -------

            """
            self.x1 = x1; self.y1 = y1
            self.x2 = x2; self.y2 = y2
            self.material = material; self.edit_mode = edit_mode
            self.group = group
            self.label1 = label1; self.label2 = label2

            femm.mi_drawrectangle(self.x1, self.y1, self.x2, self.y2)
            try:
                femm.mi_getmaterial(self.material)
            except:
                femm.mi_addmaterial(magnets[self.material][0], magnets[self.material][1], magnets[self.material][2], magnets[self.material][3], 0, magnets[self.material][4], 0, 0, 1, 0, 0, 0, 1, 0)

            femm.mi_clearselected()
            femm.mi_selectrectangle(self.x1, self.y1, self.x2, self.y2, self.edit_mode)
            femm.mi_setgroup(self.group)
            femm.mi_clearselected()
            femm.mi_addblocklabel(self.x1+self.label1, self.y2+(self.label2/2))
            femm.mi_selectlabel(self.x1+self.label1, self.y2+(self.label2/2))
            femm.mi_setblockprop(self.material, 0, 0.1, "", 90, self.group, 0)
            femm.mi_clearselected()

class Femm_move:
    def __init__(self, groups:list, x_dist, y_dist):
        """
        moves the selected groups/blocks to the specified coordinates
        __________INPUT__________
        groups : groups that need to be translated_(list)
        x_dist : target x-coordinate_(float)
        y_dist : target y-coordinate_(float)
        __________OUTPUT_______
        output : moves the selected blocks (no return values)
        """
        self.group = groups
        self.x_dist = x_dist; self.y_dist = y_dist
        for i in range(len(self.group)):
            femm.mi_selectgroup(self.group[i])
        femm.mi_movetranslate(self.x_dist, self.y_dist)
        femm.mi_clearselected()

class Femm_block():
    def __init__(self, x1, y1, x2, y2, material, edit_mode, group, label1, label2):
        """
        This method defines and creates a metal block
        ____________________INPUT_______________
        x1: x-coordinate of the edge of the rectangle [planar view of cylindrical block is a rectangle]_(float)
        y1: y-coordinate of the edge of the rectangle [planar view of cylindrical block is a rectangle]_(float)
        x2: x-coordinate of the diagonally opposite edge of (x1,y1) on the rectangle _ (float)
        y2: y-coordinate of the diagonally opposite edge of (x1,y1) on the rectangle _ (float)
        material: material of the block chosen from the FEMM library_(string)
        edit_mode:
        group: group of the block_(integer)
        label1:
        label2:
        ___________________OUTPUT______________
        models a block with the defined properties
        NO return value
        """
        self.x1 = x1; self.y1 = y1
        self.x2 = x2; self.y2 = y2
        self.material = material
        self.edit_mode = edit_mode
        self.group = group
        self.label1 = label1; self.label2 = label2

        femm.mi_drawrectangle(self.x1, self.y1, self.x2, self.y2)
        femm.mi_getmaterial(self.material)
        femm.mi_clearselected()
        femm.mi_selectrectangle(self.x1, self.y1, self.x2, self.y2, self.edit_mode)
        femm.mi_setgroup(self.group)
        femm.mi_clearselected()
        femm.mi_addblocklabel(self.x1 + (self.label1/2), self.y2 + (self.label2 / 2))
        femm.mi_selectlabel(self.x1 + (self.label1/2), self.y2 + (self.label2 / 2))
        femm.mi_setblockprop(self.material, 0, 0.1, "", 0, self.group, 0)
        femm.mi_clearselected()
class Load_coil:
    def __init__(self, coil_name):
        self.name = coil_name
        femm.mi_zoom(-2, -50, 50, 50)
        femm.mi_refreshview()
        femm.mi_saveas('LVDT position_ETpf_LIP.fem')  # We have to give the geometry a name before we can analyze it.
        femm.mi_analyze()  # Now,analyze the problem and load the solution when the analysis is finished
        femm.mi_loadsolution()
    def simulate(self):
        Coil_I, Coil_V, Coil_FluxLink = femm.mo_getcircuitproperties(self.name)
        return [Coil_I, Coil_V, Coil_FluxLink]

