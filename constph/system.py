import logging
import os
from collections import namedtuple

from typing import Tuple
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class SystemStructure(object):
    def __init__(self, configuration: dict):
        """
        A class that contains all informations for the system.
        Parameters
        ----------
        configuration: dict
            the configuration dictionary obtained with utils.load_config_yaml
        """

        self.name: str = configuration["system"]["structure"]["name"]
        self.work_dir_base: str = configuration["config"]["paths"]["work_dir"]
        self.offset: defaultdict = defaultdict(int)
        self.parameter = self._read_parameters("waterbox")
        self.cgenff_version: float
        self.envs: set
        # running a binding-free energy calculation?
        if configuration["simulation"]["free-energy-type"] == "binding-free-energy":
            self.envs = set(["complex", "waterbox"])
            for env in self.envs:
                parameter = self._read_parameters(env)
                # set up system
                self.psfs[env] = self._initialize_system(configuration, env)
                # load parameters
                self.psfs[env].load_parameters(parameter)
                # get offset
                self.offset[
                    env
                ] = self._determine_offset_and_set_possible_dummy_properties(
                    self.psfs[env]
                )

            # generate rdkit mol object of small molecule
            self.mol: Chem.Mol = self._generate_rdkit_mol(
                "complex", self.psfs["complex"][f":{self.tlc}"]
            )
            self.graph: nx.Graph = self._mol_to_nx(self.mol)

        elif configuration["simulation"]["free-energy-type"] == "solvation-free-energy":
            self.envs = set(["waterbox", "vacuum"])
            for env in self.envs:
                parameter = self._read_parameters(env)
                # set up system
                self.psfs[env] = self._initialize_system(configuration, env)
                # load parameters
                self.psfs[env].load_parameters(parameter)
                # get offset
                self.offset[
                    env
                ] = self._determine_offset_and_set_possible_dummy_properties(
                    self.psfs[env]
                )

            # generate rdkit mol object of small molecule
            self.mol: Chem.Mol = self._generate_rdkit_mol(
                "waterbox", self.psfs["waterbox"][f":{self.tlc}"]
            )
            self.graph: nx.Graph = self._mol_to_nx(self.mol)
        else:
            raise NotImplementedError(
                "only binding and solvation free energy implemented."
            )

    def _read_parameters(self, env: str) -> pm.charmm.CharmmParameterSet:
        """
        Reads in topparameters from a toppar dir and ligand specific parameters.
        Parameters
        ----------
        env: str
            waterbox,complex or vacuum
        Returns
        ----------
        parameter : pm.charmm.CharmmParameterSet
            parameters obtained from the CHARMM-GUI output dir.
        """

        # the parameters for the vacuum system is parsed from the waterbox charmm-gui directory
        if env == "vacuum":
            env = "waterbox"

        charmm_gui_env = self.charmm_gui_base + env
        tlc = self.tlc
        tlc_lower = str(tlc).lower()
        toppar_dir = get_toppar_dir()

        # if custom parameter are added they are located in l1,l2
        parameter_files = tuple()
        l1 = f"{charmm_gui_env}/{tlc_lower}/{tlc_lower}.rtf"
        l2 = f"{charmm_gui_env}/{tlc_lower}/{tlc_lower}.prm"

        for file_path in [l1, l2]:
            if os.path.isfile(file_path):
                parameter_files += (file_path,)
            else:
                logger.critical(
                    f"Custom ligand parameters are not present in {file_path}"
                )

        # check cgenff versions
        if parameter_files:
            with open(parameter_files[0]) as f:
                _ = f.readline()
                cgenff = f.readline().rstrip()
                logger.info(f"CGenFF version: {cgenff}")
                cgenff_version = re.findall("\d+\.\d+", cgenff)[0]
                self.cgenff_version = float(cgenff_version)

        parameter_files += (f"{toppar_dir}/top_all36_prot.rtf",)
        parameter_files += (f"{toppar_dir}/par_all36m_prot.prm",)
        parameter_files += (f"{toppar_dir}/par_all36_na.prm",)
        parameter_files += (f"{toppar_dir}/top_all36_na.rtf",)
        parameter_files += (f"{toppar_dir}/top_all36_cgenff.rtf",)
        parameter_files += (f"{toppar_dir}/par_all36_cgenff.prm",)
        parameter_files += (f"{toppar_dir}/par_all36_lipid.prm",)
        parameter_files += (f"{toppar_dir}/top_all36_lipid.rtf",)
        parameter_files += (f"{toppar_dir}/toppar_water_ions.str",)

        # set up parameter objec
        parameter = pm.charmm.CharmmParameterSet(*parameter_files)
        return parameter

    def _initialize_system(self, configuration: dict, env: str) -> pm.charmm.CharmmPsfFile:
        """
        Generates the psf file and sets the coordinates from the CHARMM-GUI files.
        Parameters
        ----------
        configuration: dict
            the configuration dictionary obtained with utils.load_config_yaml
        env: str
            waterbox,complex or vacuum
        Returns
        ----------
        psf : pm.charmm.CharmmPsfFile
        """

        if env == "vacuum":
            # take the structures from the waterbox system and extract only the ligand
            taken_from = "waterbox"
            psf_file_name = configuration["system"][self.structure][taken_from][
                "psf_file_name"
            ]
            crd_file_name = configuration["system"][self.structure][taken_from][
                "crd_file_name"
            ]

            psf_file_path = (
                f"{self.charmm_gui_base}/{taken_from}/openmm/{psf_file_name}.psf"
            )
            crd_file_path = (
                f"{self.charmm_gui_base}/{taken_from}/openmm/{crd_file_name}.crd"
            )
            psf = pm.charmm.CharmmPsfFile(psf_file_path)
            coord = pm.charmm.CharmmCrdFile(crd_file_path)
            psf.coordinates = coord.coordinates
            # extract only ligand to generate vacuum system
            psf = psf[f":{self.tlc}"]
        else:
            psf_file_name = configuration["system"][self.structure][env][
                "psf_file_name"
            ]
            crd_file_name = configuration["system"][self.structure][env][
                "crd_file_name"
            ]

            psf_file_path = f"{self.charmm_gui_base}/{env}/openmm/{psf_file_name}.psf"
            crd_file_path = f"{self.charmm_gui_base}/{env}/openmm/{crd_file_name}.crd"
            psf = pm.charmm.CharmmPsfFile(psf_file_path)
            coord = pm.charmm.CharmmCrdFile(crd_file_path)
            psf.coordinates = coord.coordinates

        return psf

    def _determine_offset_and_set_possible_dummy_properties(self, psf: pm.charmm.CharmmPsfFile) -> int:
        """
        Determines the offset and sets possible properties on the psf.
        Parameters
        ----------
        psf : pm.charmm.CharmmPsfFile
        env: str
            waterbox,complex or vacuum
        Returns
        ----------
        """
        assert type(psf) == pm.charmm.CharmmPsfFile
        if len(psf.view[f":{self.tlc}"].atoms) < 1:
            raise RuntimeError(f"No ligand selected for tlc: {self.tlc}")

        psf.number_of_dummys = 0
        psf.mutations_to_default = 0

        idx_list = []
        for atom in psf.view[f":{self.tlc}"].atoms:
            idx_list.append(int(atom.idx))

            # charge, epsilon and rmin are directly modiefied
            atom.initial_charge = atom.charge
            atom.initial_epsilon = atom.epsilon
            atom.initial_rmin = atom.rmin

        return min(idx_list)