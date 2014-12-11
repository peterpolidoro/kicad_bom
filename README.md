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

###Linux and Mac OS X

[Setup Python for Linux](./PYTHON_SETUP_LINUX.md)

[Setup Python for Mac OS X](./PYTHON_SETUP_MAC_OS_X.md)

```shell
mkdir -p ~/virtualenvs/kicad
virtualenv ~/virtualenvs/kicad
source ~/virtualenvs/kicad/bin/activate
pip install kicad_bom
```

###Windows

[Setup Python for Windows](./PYTHON_SETUP_WINDOWS.md)

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

