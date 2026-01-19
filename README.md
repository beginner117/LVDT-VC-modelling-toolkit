# 🧲 FEMM-Based Simulation Toolkit for LVDTs & VCs 
This repository provides a modular Python interface to simulate Linear Variable Differential Transformers (LVDTs) and Voice Coils (VCs), including custom geometries used in the ETpathfinder project. Simulations are powered by **FEMM** (Finite Element Method Magnetics), with Python integration via the `pyFEMM` package—eliminating the need for LabVIEW or other GUI-based tools.

> ⚠️ **Note:** FEMM is Windows-only. This repository will only work on **Windows systems** with FEMM installed.
## 🚀 Quick Start
Below, you will find some short instructions on how to install the software. 

    Install the FEMM software on your Windows machine: https://www.femm.info/wiki/HomePage Go to download page and follow instructions.
    Assuming you have a working python 3.10.1 version, install pyFEMM: https://www.femm.info/wiki/pyFEMM. You can do this with pip via: pip install pyfemm. On the linked page you can also find the pyFEMM manual.
🍎 Mac Users

    For Mac users, install Whisky or Wine (Whisky for new ARM mac) followed by installing femm 42. Find the path of femm.exe and update the text file named 'femmpath.txt' with the path. The default text file contains an example path. 
    (put it in git ignore after modification). 

Installing virtual environment

    python version 3.10.1

Installing dependencies:

    pip install -r requirements.txt

example 

    The file 'example_simulation.py' contains the basic information and instructions to run the simulation.
    Run this file to simulate LVDTs by changing the instances/arguments as per the requirements

Interactive GUI
    
    run the file 'finite_element_simulation.py' for opening a graphic interface. 

file paths 

    >> import sys
    >> sys.append(<include the path of the femm_sim>)

Here is the list of modules:

    feed.py - contains the dimensions of preliminary NIKHEF designs and wire types used
    design.py - contains all the classes that returns the coil geometry
    coil.py - contains all the classes that returns coil properties  
    femm_model.py - contains the classes that models the coils, magnets in FEMM
    fields.py - contains the classes that calculates the magnetic fields, voltages, forces by numerical methods (using the field information from FEMM)
    LVDT.py - contains the script that simulates a typical LVDT used in pathfinder
    VC.py - contains the script that simulates a typical VC used in pathfinder
    VC_only.py - contains the script that simulates a typical VC-only used in pathfinder
    YOKE.py - contains the script that simulates a complicated YOKE structure used in pathfinder
    LVDT_mutual_inductance.py - contains the script that calculates the mutual inductance between the coils of the LVDT
    LVDT_correction.py - contains the script that calculates the correction factor (needed due to open circuit simulation in FEMM) of LVDT response  
    femm_simulation.py - contains all the methods that call and execute LVDT and VC simulations using FEMM
    analytical_simulation - contains all the methods that call and execute LVDT and VC simulations analytically
    single_coil.py - models a single coil

Here is a explanation for simulating a typical LVDT/VC. One can model one or more sensors simultaneously

    sim_code = femm_simulation.Position_sensor(sensor_type = ['LVDT'], save = True, sim_range = {'steps_size_offset': [[1, 0.5, -0.5]]},
               data = {'filename(s)': ['I_long'], 'is default': ['yes'], 'design or parameter': ['A']},
               material_prop = ['32 AWG', '32 AWG', "N40"], dimensions = {'inner':[24, 11, 6], 'outer':[13.5, 35, 5, 54.5], 'magnet':[40, 10]}, 
               boundary = [150, 'Air', 0.5, 300, 'Air', 1, 'Outside'])

    a = sim_code.execute()


    ______INPUT_______
    sensor_type = list with names of sensors that should be simulated
    save = 'True' to save all the simulated files or 'False' to not save the files
    sim_range = list containg a list (nested list) of total steps, grid size and offset
    filename(s) = name(s) of the simulated file(s) 
    is default = 'yes' if the simulation is for a default ETpathfinder design and 'no' if not
    design or parameter = list with design type (if 'is default' is 'yes') or a random string (if 'is default is 'no')
    material_prop = list containing (i) inner coil material (ii) outer coil material (iii) magnet material
    dimensions = dictionary with the coil geometry with 'inner', 'outer', 'magnet' as keys and corresponding dimensions (in mm)in lists as values.
               Values of the keys are height, radius, layers, distance (for the 'outer') in mm for the coils and length, diameter (in mm) for the magnet
               Example - {'inner':[24, 11, 6], 'outer':[13.5, 35, 7, 54.5], 'magnet':[40, 10]}
    boundary = list containing boundary radius, name, and mesh size (in this order) of two air space regions
    
OPTIONAL

    material_prop = list containing (i) inner coil material (ii) outer coil material (iii) magnet material
    dimensions = dictionary with the coil geometry with 'inner', 'outer', 'magnet' as keys and corresponding dimensions (in mm)in lists as values.
               Values of the keys are height, radius, layers, distance (for the 'outer') in mm for the coils and length, diameter (in mm) for the magnet
               Example - {'inner':[24, 11, 6], 'outer':[13.5, 35, 7, 54.5], 'magnet':[40, 10]}
        (In simulations using the above 'dimensions' argument, make sure to input 'no' to the argument 'is default' and any random string for the argument 'design or parameter'
    simulation_type = list with strings 'semi_analytical' for analytical calculation

               NOTE - Alternatively, this geometry can also be defined in the 'feed.py' module with the apropriate name following the order of the existing designs in that module. 
               MOST IMPORTANT, add the defined design as a value and your choice of name(for that design) as a key in the dictionary 'data' to call it directly with the name.
    
    ARGUMENTS IN THE 'execute' METHOD 
    input_current : list with Inner coil current(in amps), frequency(in Hz), outer coil(upper and lower in a tuple) currents
    (Default values for LVDT is [0.02, 10000, [0,0]] and for VC is [0, 0, [1,1]])
    
    _______OUTPUT______
    saves all the data along with the simulation parameters in a .npz file (if the save argument above is True)

Here are the default assumptions

    wire material - 32 AWG
    magnet type - N40
    Inner coil excitation (for LVDT) - 10 kHz, 20 mA sinusoidal wave
    Outer coil excitation (for VC, VC_only) - 1A DC
    Units - millimeters
    precision - 1.0e-10

            Boundary conditions 

    material - Air
    Region 1 - sphere with radius 150mm, mesh size : 0.5
    Region 2 - sphere with radius 300mm, mesh size : 1
    

NOTE1 - Make sure the modified/newly added material above is available in the FEMM material library. If not, the new material must be defined with all the properties in the 'feed.py' module.

NOTE2 - A lot of other information like resistances, currents e.t.c are obtained from the simulation. To know them, load the saved '.npz' file and look for all the data


For a better understanding, a model code to simulate LVDTs is given in 'example.md' file. Please go through that.   






