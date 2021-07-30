from dataclasses import dataclass

#dataclass
@dataclass
class parameters:
    nstep: int
    nstdcd: int
    nstout: int
    cons: str
    dt: float
@dataclass
class production_run:
    parameters: parameters
@dataclass
class parameters:
    nstep: int
    nstdcd: int
    nstout: int
    cons: str
    dt: float
@dataclass
class search_run:
    parameters: parameters
@dataclass
class structure:
    name: str
    MD: str
    bb: str
@dataclass
class system:
    structure: structure
    name: str
@dataclass
class input_dataclass:
    system: system
    search_run: search_run
    production_run: production_run
    bin_dir: str
    analysis_dir_base: str
    data_dir_base: str
    system_dir: str
    cluster_dir: str
