
# Python Package directories
setenv FEB_DIR    ${PWD}/../firmware/common/AtlasChess2Feb
setenv SURF_DIR   ${PWD}/../firmware/submodules/surf
setenv ROGUE_DIR  ${PWD}/rogue

# Setup enivorment
# with SLAC AFS access
source /afs/slac.stanford.edu/g/reseng/python/3.5.2/settings.csh
source /afs/slac.stanford.edu/g/reseng/boost/1.62.0_p3/settings.csh

# with local installations
#source /path/to/python/3.5.2/settings.csh
#source /path/to/boost/1.62.0/settings.csh

# Setup python path
setenv PYTHONPATH ${PWD}/python:${SURF_DIR}/python:${FEB_DIR}/python:${ROGUE_DIR}/python

# Setup library path
setenv LD_LIBRARY_PATH ${ROGUE_DIR}/python::${LD_LIBRARY_PATH}


# SLAC setup-------------------
setenv ROOTSYS /afs/slac.stanford.edu/g/atlas/packages/root/proof
setenv PYTHIA8 /u/at/pnef/Work/Code/pythia8183
setenv XPDUTILS ${ROOTSYS}/etc/proof/utils
setenv PATH ${ROOTSYS}/bin:${PATH}
setenv PATH ${PATH}:~/local/bin
setenv LD_LIBRARY_PATH ${PYTHIA8}/lib:${ROOTSYS}/lib:${ROOTSYS}/bin/root:${LD_LIBRARY_PATH}
setenv DYLD_LIBRARY_PATH ${ROOTSYS}/lib:${ROOTSYS}/bin/root
setenv PYTHONPATH ${ROOTSYS}/lib:${PYTHONPATH}

