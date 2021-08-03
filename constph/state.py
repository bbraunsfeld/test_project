import logging
import os
import shutil
from io import StringIO


import constph

from constph.gromos_factory import GromosFactory
from typing import List

logger = logging.getLogger(__name__)


class StateFactory(object):
    def __init__(
        self, system: constph.system.SystemStructure, configuration: dict
    ):
        """
        Generate the directories for the search and production runs for the provided systems.
        Parameters
        ----------
        system : constph.system
            definition of the two end states for a given system
        configuration : dict
            configuration dictionary
        """

        self.system = system
        self.path = f"{configuration['system_dir']}/{self.system.name}"
        self._init_base_dir()
        self.configuration = configuration
        self.vdw_switch: str
        self.charmm_factory = GromosFactory(configuration, self.system.structure)
    
    def _get_simulations_parameters(self):
        prms = {}
        for key in self.configuration["simulation"]["parameters"]:
            prms[key] = self.configuration["simulation"]["parameters"][key]
        return prms
    
    
    def _copy_files(self, intermediate_state_file_path: str):
        """
        Copy the files from the original CHARMM-GUI output folder in the intermediate directories.
        """

        basedir = self.system.charmm_gui_base

        self._copy_ligand_specific_top_and_par(basedir, intermediate_state_file_path)

        # copy central toppar folder
        toppar_dir = get_toppar_dir()
        toppar_source = f"{toppar_dir}"
        toppar_target = f"{intermediate_state_file_path}/toppar"
        shutil.copytree(toppar_source, toppar_target)

        # copy crd file
        self._copy_crd_file((intermediate_state_file_path))

        # copy openMM and charmm specific scripts
        self._copy_omm_files(intermediate_state_file_path)
        self._copy_charmm_files(intermediate_state_file_path)   
   
   
    def _init_base_dir(self):
        """
        Generates the base directory which all intermediate states are located.
        """

        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
            os.makedirs(self.path)
        else:
            os.makedirs(self.path)

    def _init_intermediate_state_dir(self, nr: int):
        """
        Generates the intermediate state directory.
        """
        output_file_base = f"{self.path}/intst{nr}/"

        logger.info(f" - Created directory: - {os.path.abspath(output_file_base)}")
        os.makedirs(output_file_base)
        logger.info(f" - Writing in - {os.path.abspath(output_file_base)}")
        return output_file_base