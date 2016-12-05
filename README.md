# atlas-chess2
Project for ATLAS CHESS2 ASIC Development

The atlas-chess2 project can be found at:

https://github.com/slaclab/atlas-chess2

To checkout atlas-chess2 and all submodules:

> git clone git@github.com:slaclab/atlas-chess2 --recursive

> git strack

# How to build PGP Firmware/Software

To build the firmware

> cd atlas-chess2/firmware

> source setup_template.csh

> cd targets/AtlasChess2FebPgp

> make

To build and run the software

> cd atlas-chess2/software/rogue/

> source setup_template.csh

> make 

> cd ..

> source setup_template.csh

> make 

> python scripts/FebGuiPgp.py
