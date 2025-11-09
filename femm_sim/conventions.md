This document is for editing the modules, classes which are imported by default in the main running file.

This file contains the standard conventions, some are from FEMM itself which cannot be altered and some written by me which can be altered, used the script to define materials, design parameters e.t.c

Defining the design dimensions
    
    The design (dimensions) should be defined as a dictionary in the 'feed' module. (All the NIKHEF LVDT, VC designs are pre defined)
    It is straight forward to add a new design. Follow the convention and order used in the feed module. 
    NOTE - Add the defined design as a value and your choice of name(for that design) as a key in the dictionary 'data'. Else, script will not run.  
      

Defining the wire properties 

    wire types should be added as a new key in the dictionary 'wire_types' in the 'feed' module. Some commonly used wires are pre defined. 
    key - [parameter1, parameter2, ...]

    Each key in the dictionary represents a specific wire and contains the list of required parameters in sequence as values. Initial 4 parameters(upto resistance) are mandatory and the rest are optional. 
    Here is an example:
    Wire_name(str) : [wire_dia(in mm), insulation_thickness(in mm), name of your choice(str), resistance(Ω/mm), electrical_conductivity(MS/m), resistivity(Ω*m), magnetic_perm(H/m)]
    

Adding the new materials (these details can also be found in the pyfemm manual)

    use the command 'femm.mi_addmaterial()' in the class 'Femm_coil' in the module 'femm_model' and pass the following arguments 
    
    argument1: MATERIAL NAME (string) - name of the material you specified while defining the wire properties
    argument2: MU_X (float) - relative permeability in X or radial direction
    argument3: MU_Y (float) - relative permeability in Y or Z direction
    argument4: Hc (float) - Permenant magnet coercivity (A/m)
    argument5: J (float) - Source current density (A/mm^2)
    argument6: C (float) - electrical conductivity (MS/m)
    argument7: Lam d (float) - Lamination thickness (mm)
    argument8: Phi_max (float) - Hysterisis lag (non linear BH curve)
    argument9: Lam fill fraction (float) - volume occupied per lamination that is actually filled with iron (Note that this parameter defaults to 1 in the femm preprocessor dialog box because, by default,iron completely fills the volume
    argument10: Lam type (integer) - 0 – Not laminated or laminated in plane
                                     1 – laminated x or r, 2 – laminated y or z
                                     3 – magnet wire, 4 – plain stranded wire
                                     5 – Litz wire, 6 – square wire
    argument11: Phi_hx (float) - Hysteresis lag in degrees in the x-direction for linear problems
    argument12: Phi_hy (float) - Hysteresis lag in degrees in the y-direction for linear problems
    argument13: nstr (integer) - Number of strands in the wire build. Should be 1 for Magnet or Square wire
    argument14: dwire (float) - bare wire diameter (mm)

Defining the extra structure (with ferro/dia magnetic materials) around LVDT/VC. 
2 NIKHEF designs already exist with such extra yoke structure. The extra structure must be defined as set of rectangular blocks. 
    