import numpy as np

from calculator.calculator import Calculator
from matter.atoms import AtomsInBox
from matter.utils import AllInOneSampler

from field.electromagnetic import FreeVectorPotential,CavityVectorPotential
#from field.utils import EM_mode_generate_,EM_mode_generate, EM_mode_generate3

import utilities.reduced_parameter as red

####################
### DRIVER PARAM ###
####################

num_cycles = 20
#if num_cycles != 20: print("Warning, number of cycles is not 10!")

h = 1e-2

################
### BOX SIZE ### 
################

l = 3
Lxy = l * 1e7
Lz  = l * 1e7

Lz_red  = l * 1e3
zlabel = 'microz'

Lxy_double  = l * 2e7
xlabel2 = 'doublex'
##############
### MATTER ###
##############

N_atom_pairs = 512

mu0 = red.mu0

cw_get = lambda L: np.max((L/1e2, 10))

def initiate_atoms_box(Lxy, Lz):
    """
    Generate an empty atom box with no atoms.
    Args:
    + Lxy (float): 
    + Lz (float):
    """
    atoms = AtomsInBox(
        Lxy = Lxy, Lz= Lz, cell_width = (cw_get(Lxy), cw_get(Lz)), 
        mass_dict = red.mass_dict)
    # Generate a matrix of LJ potential parameter
    # e.g. matrix P with Pij is LJ parameter for i- and j-th atoms
    idxAr = [1]*N_atom_pairs + [0]*N_atom_pairs # atoms.element_idx(element = "Xe")
    idxXe = [0]*N_atom_pairs + [1]*N_atom_pairs # atoms.element_idx(element = "Ar")
    epsilon_mat, sigma_mat = red.generate_LJparam_matrix(idxAr = idxAr, idxXe = idxXe)

    # calculator to the atoms object
    atoms.add_calculator(
        calculator_class = Calculator, N_atoms = N_atom_pairs * 2,
        calculator_kwargs = {
            "epsilon": epsilon_mat, "sigma" : sigma_mat, 
            "positive_atom_idx" : idxXe, "negative_atom_idx" : idxAr,
            "mu0" : mu0, "d" : red.d0, "a" : red.a, "d7": red.d7
        })

    return atoms

#############
### FIELD ### 
#############

default_kvector_int = np.array(
        [[i,0,0] for i in range(1,260)]\
       #+[[0,i,0] for i in range(1,150)]
       #+[[0,0,i] for i in range(1,180)]
        )

coupling_strength_dict = {
        "Lxy": Lxy,
        "Lxy5": Lxy * 5,
        "Lxy1e1": Lxy * 1e1,
        "Lxy1e1s": Lxy * 1e1 * np.sqrt(2),
        "Lxy15": Lxy * 15,
        "Lxy2e1": Lxy * 2e1,
        "Lxy2e1s": Lxy * 2e1 * np.sqrt(2),
        "Lxy3e1": Lxy * 3e1,
        "Lxy4e1": Lxy * 4e1,
        }

C = np.sqrt(Lxy * Lxy * Lz)
dC = C * 1e-1

def generate_field_amplitude(kvector_int, mode):
    if mode == "zero":
        amplitude = np.zeros(
            (len(kvector_int), 2), dtype = np.complex128)
    elif mode == "zpve":
        amplitude = np.sqrt(red.hbar * 2 * np.pi) * np.exp(
                1j * 2 * np.pi * np.random.rand(len(kvector_int), 2)
                )
    elif mode == 'config':
        k_val = np.sqrt(np.einsum("ki,ki->k",kvector_int, kvector_int))
        k_val = np.tile(k_val[:,np.newaxis],(1,2))

        amplitude = np.vstack([
            np.random.uniform(low=C-dC, high=C+dC, size = 2) * 1 \
                    + np.random.uniform(low=C-dC, high=C+dC,size = 2) * 1j
            for i in range(len(ext_mode_int))
            ])  * k_val**-1 

    return amplitude
