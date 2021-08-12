from dataclasses import dataclass

#dataclass
@dataclass
class production_parameters:
    nstep: int
    nstdcd: int
    nstout: int
    cons: str
    dt: float
@dataclass
class production_run:
    production_parameters: production_parameters
@dataclass
class search_parameters:
    NSTLIM: int
    NTWX: int
    NTWE: int
    cons: str
    dt: float
@dataclass
class search_run:
    search_parameters: search_parameters
@dataclass
class specs:
    lib_template: str
    program_version: str
    joblist: str
@dataclass
class paths:
    gromos_bin: str
    work_dir: str
@dataclass
class config:
    paths: paths
    specs: specs
@dataclass
class structure:
    name: str
    topo: str
    coord: str
    pttopo: str
@dataclass
class system:
    structure: structure
    name: str
@dataclass
class input_dataclass:
    system: system
    config: config
    search_run: search_run
    production_run: production_run
    bin_dir: str
    analysis_dir_base: str
    data_dir_base: str
    system_dir: str
