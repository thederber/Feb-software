
# Python Package directories
export ATLAS_REPO_DIR=/usr/local/chess2/chess2/atlas-chess2
export FEB_DIR=${ATLAS_REPO_DIR}/firmware/common/AtlasChess2Feb
export SURF_DIR=${ATLAS_REPO_DIR}/firmware/submodules/surf
export ROGUE_DIR=${ATLAS_REPO_DIR}/software/rogue


# Setup environment
# with SLAC AFS access
#source /afs/slac.stanford.edu/g/reseng/python/3.5.2/settings.sh
#source /afs/slac.stanford.edu/g/reseng/boost/1.62.0_p3/settings.sh

# with local installations
source /usr/local/python/Python-3.6.5/settings.sh
source /usr/local/boost/1.64.0/settings.sh

# Setup python path
export PYTHONPATH=${PWD}/python:${SURF_DIR}/python:${FEB_DIR}/python:${ROGUE_DIR}/python

# Setup library path
export LD_LIBRARY_PATH=${ROGUE_DIR}/python::${LD_LIBRARY_PATH}


export MPLBACKEND=Qt4Agg
