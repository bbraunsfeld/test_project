import datetime
from os import stat

class GromosFactory:
    """Class to build the string needed to create a Gromos input file (*.imd), a make_script fiel (*.arg) and a job file (*.job)"""

    def __init__(self, configuration: dict, structure: str) -> None:

        self.configuration = configuration
        self.structure = structure

    def _get_search_run_parameters(self):
        prms = {}
        for key in self.configuration["search_run"]["search_parameters"]:
            prms[key] = self.configuration["search_run"]["search_parameters"][key]
        return prms

    def _get_production_run_parameters(self):
        prms = {}
        for key in self.configuration["production_run"]["production_parameters"]:
            prms[key] = self.configuration["production_run"]["production_parameters"][key]
        return prms


    def generate_Gromos_search_input(self, env: str) -> str:

        gromos_search_script = self._get_Gromos_input_header(env)
        if env == "search":
            gromos_search_script += (
                self._get_Gromos_search_body()
            )
        else:
            raise NotImplementedError(f"Something went wrong with {env} input.")

        return gromos_search_script

    def generate_Gromos_production_input(self, env: str) -> str:

        gromos_search_script = self._get_Gromos_input_header(env)
        if env == "production":
            gromos_search_script += (
                self._get_Gromos_production_body()
            )
        else:
            raise NotImplementedError(f"Something went wrong with {env} input.")

        return gromos_search_script

    def _get_Gromos_input_header(self, env: str) -> str:
        date = datetime.date.today()
        header = f"""TITLE
Automatically generated input file for {env} run with constph
Version {date}
END
"""
        return header
        
    def _get_Gromos_search_body(self) -> str:

        NSM = self.configuration["search_run"]["search_parameters"]["NSM"]
        NSTLIM = self.configuration["search_run"]["search_parameters"]["NSTLIM"]
        DT = self.configuration["search_run"]["search_parameters"]["dt"]
        ATMNR1 = self.configuration["search_run"]["search_parameters"]["ATMNR1"]
        ATMNR2 = self.configuration["search_run"]["search_parameters"]["ATMNR2"]
        NTWX = self.configuration["search_run"]["search_parameters"]["NTWX"]
        NTWE = self.configuration["search_run"]["search_parameters"]["NTWE"]
        FORM = "4"
        NSTATES = self.configuration["search_run"]["search_parameters"]["NSTATES"]
        OFFSETS = "0   " * int(NSTATES)
        SIGMA = self.configuration["search_run"]["search_parameters"]["sigma"] 
        ASTEPS = self.configuration["search_run"]["search_parameters"]["asteps"]
        BSTEPS = self.configuration["search_run"]["search_parameters"]["bsteps"]
        
        body = f"""SYSTEM
#      NPM      NSM
         1     {NSM}
END
STEP
#   NSTLIM         T        DT
   {NSTLIM}        0      {DT}
END
BOUNDCOND
#      NTB    NDFMIN
         1         3
END
MULTIBATH
# NTBTYP:
#      weak-coupling:      use weak-coupling scheme
#      nose-hoover:        use Nose Hoover scheme
#      nose-hoover-chains: use Nose Hoover chains scheme
# NUM: number of chains in Nose Hoover chains scheme
#      !! only specify NUM when needed !!
# NBATHS: number of temperature baths to couple to
#          NTBTYP
                   0
#  NBATHS
         2
# TEMP0(1 ... NBATHS)  TAU(1 ... NBATHS)
       300       0.1
       300       0.1

#   DOFSET: number of distinguishable sets of d.o.f.
         2
# LAST(1 ... DOFSET)  COMBATH(1 ... DOFSET)  IRBATH(1 ... DOFSET)
    {ATMNR1}         1         1      {ATMNR2}         2         2
END
PRESSURESCALE
# COUPLE   SCALE    COMP    TAUP  VIRIAL
       2       1 0.0007624      0.5        2
# SEMIANISOTROPIC COUPLINGS(X, Y, Z)
       1        1        2
# PRES0(1...3,1...3)
 0.06102       0       0
       0 0.06102       0
       0       0 0.06102
END
FORCE
#      NTF array
# bonds    angles   imp.     dihe     charge nonbonded
  0        1        1        1        1        1
# NEGR    NRE(1)    NRE(2)    ...      NRE(NEGR)
     2
    {ATMNR1}     {ATMNR2}
END
COVALENTFORM
#    NTBBH    NTBAH     NTBDN
         0         0         0
END
CONSTRAINT
# NTC
    3
#      NTCP  NTCP0(1)
          1    0.0001
#      NTCS  NTCS0(1)
          1    0.0001
END
PAIRLIST
# algorithm    NSNB   RCUTP   RCUTL    SIZE    TYPE
          1       5     0.8     1.4     0.4       0
END
NONBONDED
# NLRELE
         1
#  APPAK    RCRF   EPSRF    NSLFEXCL
         0       1.4      78.5         1
# NSHAPE  ASHAPE  NA2CLC   TOLA2   EPSLS
         3       1.4         2     1e-10         0
#    NKX     NKY     NKZ   KCUT
        10        10        10       100
#    NGX     NGY     NGZ  NASORD  NFDORD  NALIAS  NSPORD
        32        32        32         3         2         3         4
# NQEVAL  FACCUR  NRDGRD  NWRGRD
    100000       1.6         0         0
#  NLRLJ  SLVDNS
         0      33.3
END
INITIALISE
# Default values for NTI values: 0
#   NTIVEL    NTISHK    NTINHT    NTINHB
         0         0         0         0
#   NTISHI    NTIRTC    NTICOM
         0         0         0
#   NTISTI
         0
#       IG     TEMPI
    210185         0
END
COMTRANSROT
#     NSCM
      1000
END
PRINTOUT
#NTPR: print out energies, etc. every NTPR steps
#NTPP: =1 perform dihedral angle transition monitoring
#     NTPR      NTPP
       500         0
END
WRITETRAJ
#    NTWX     NTWSE      NTWV      NTWF      NTWE      NTWG      NTWB
    {NTWX}         0         0         0     {NTWE}        0         0
END
AEDS
#     AEDS
         1
#   ALPHLJ   ALPHCRF      FORM      NUMSTATES
         0         0      {FORM}    {NSTATES}
#     EMAX      EMIN
        0          0
# EIR [1..NUMSTATES]
        {OFFSETS}
# NTIAEDSS  RESTREMIN  BMAXTYPE      BMAX    ASTEPS    BSTEPS
         1          1   {SIGMA}         2    {ASTEPS}  {BSTEPS}
END"""

        return body


    def _get_Gromos_production_body(self) -> str:

        NSM = self.configuration["production_run"]["_parameters"]["NSM"]
        NSTLIM = self.configuration["production_run"]["production_parameters"]["NSTLIM"]
        DT = self.configuration["production_run"]["production_parameters"]["dt"]
        ATMNR1 = self.configuration["production_run"]["production_parameters"]["ATMNR1"]
        ATMNR2 = self.configuration["production_run"]["production_parameters"]["ATMNR2"]
        NTWX = self.configuration["production_run"]["production_parameters"]["NTWX"]
        NTWE = self.configuration["production_run"]["production_parameters"]["NTWE"]
        FORM = "4"
        NSTATES = self.configuration["production_run"]["production_parameters"]["NSTATES"]
        OFFSETS = "0   {new_offset}"
        SIGMA = self.configuration["production_run"]["production_parameters"]["sigma"] 
        EMIN = "found in search"
        EMAX = "found in search"

        body = f"""SYSTEM
#      NPM      NSM
         1     {NSM}
END
STEP
#   NSTLIM         T        DT
   {NSTLIM}        0      {DT}
END
BOUNDCOND
#      NTB    NDFMIN
         1         3
END
MULTIBATH
# NTBTYP:
#      weak-coupling:      use weak-coupling scheme
#      nose-hoover:        use Nose Hoover scheme
#      nose-hoover-chains: use Nose Hoover chains scheme
# NUM: number of chains in Nose Hoover chains scheme
#      !! only specify NUM when needed !!
# NBATHS: number of temperature baths to couple to
#          NTBTYP
                   0
#  NBATHS
         2
# TEMP0(1 ... NBATHS)  TAU(1 ... NBATHS)
       300       0.1
       300       0.1

#   DOFSET: number of distinguishable sets of d.o.f.
         2
# LAST(1 ... DOFSET)  COMBATH(1 ... DOFSET)  IRBATH(1 ... DOFSET)
    {ATMNR1}         1         1      {ATMNR2}         2         2
END
PRESSURESCALE
# COUPLE   SCALE    COMP    TAUP  VIRIAL
       2       1 0.0007624      0.5        2
# SEMIANISOTROPIC COUPLINGS(X, Y, Z)
       1        1        2
# PRES0(1...3,1...3)
 0.06102       0       0
       0 0.06102       0
       0       0 0.06102
END
FORCE
#      NTF array
# bonds    angles   imp.     dihe     charge nonbonded
  0        1        1        1        1        1
# NEGR    NRE(1)    NRE(2)    ...      NRE(NEGR)
     2
    {ATMNR1}     {ATMNR2}
END
COVALENTFORM
#    NTBBH    NTBAH     NTBDN
         0         0         0
END
CONSTRAINT
# NTC
    3
#      NTCP  NTCP0(1)
          1    0.0001
#      NTCS  NTCS0(1)
          1    0.0001
END
PAIRLIST
# algorithm    NSNB   RCUTP   RCUTL    SIZE    TYPE
          1       5     0.8     1.4     0.4       0
END
NONBONDED
# NLRELE
         1
#  APPAK    RCRF   EPSRF    NSLFEXCL
         0       1.4      78.5         1
# NSHAPE  ASHAPE  NA2CLC   TOLA2   EPSLS
         3       1.4         2     1e-10         0
#    NKX     NKY     NKZ   KCUT
        10        10        10       100
#    NGX     NGY     NGZ  NASORD  NFDORD  NALIAS  NSPORD
        32        32        32         3         2         3         4
# NQEVAL  FACCUR  NRDGRD  NWRGRD
    100000       1.6         0         0
#  NLRLJ  SLVDNS
         0      33.3
END
INITIALISE
# Default values for NTI values: 0
#   NTIVEL    NTISHK    NTINHT    NTINHB
         0         0         0         0
#   NTISHI    NTIRTC    NTICOM
         0         0         0
#   NTISTI
         0
#       IG     TEMPI
    210185         0
END
COMTRANSROT
#     NSCM
      1000
END
PRINTOUT
#NTPR: print out energies, etc. every NTPR steps
#NTPP: =1 perform dihedral angle transition monitoring
#     NTPR      NTPP
       500         0
END
WRITETRAJ
#    NTWX     NTWSE      NTWV      NTWF      NTWE      NTWG      NTWB
    {NTWX}         0         0         0     {NTWE}        0         0
END
AEDS
#     AEDS
         1
#   ALPHLJ   ALPHCRF      FORM      NUMSTATES
         0         0      {FORM}    {NSTATES}
#     EMAX      EMIN
      {EMAX}    {EMIN}
# EIR [1..NUMSTATES]
        {OFFSETS}
# NTIAEDSS  RESTREMIN  BMAXTYPE      BMAX    ASTEPS    BSTEPS
         1          1   {SIGMA}         2         0         0 
END"""

        return body


