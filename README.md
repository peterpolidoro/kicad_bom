kicad_bom
=========

KiCad Python module for generating bill of materials in multiple
formats.

Authors:

    Peter Polidoro <peterpolidoro@gmail.com>
    Jean-Pierre Charras <jean-pierre.charras[at]gipsa-lab-dot-inpg-dot-fr>

Package Maintainers:

    Peter Polidoro <peterpolidoro@gmail.com>

License:

    GPL

##Installation

[Setup Python](https://github.com/janelia-pypi/python_setup)

###Linux and Mac OS X

```shell
mkdir -p ~/virtualenvs/kicad
virtualenv ~/virtualenvs/kicad
source ~/virtualenvs/kicad/bin/activate
pip install kicad_bom
```

###Windows

```shell
virtualenv C:\virtualenvs\kicad
C:\virtualenvs\kicad\Scripts\activate
pip install kicad_bom
```

##Command Line Use

###Linux and Mac OS X

```shell
source ~/virtualenvs/kicad/bin/activate
kicad_bom <netlist.xml>
```

###Windows

```shell
C:\virtualenvs\kicad\Scripts\activate
kicad_bom <netlist.xml>
```

