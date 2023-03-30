- [About](#orgb39bbb1)
- [Example Usage](#orgf3dbf7d)
- [Installation](#orgdd67935)
- [Development](#orgfcd8cca)

    <!-- This file is generated automatically from metadata -->
    <!-- File edits may be overwritten! -->


<a id="orgb39bbb1"></a>

# About

```markdown
- Python Package Name: kicad_bom
- Description: KiCad Python code for generating bill of materials in multiple formats.
- Python Package Exports: KicadBom, save_all_csv_files
- Version: 5.0.1
- Python Version: 3.9
- Release Date: 2023-03-30
- Creation Date: 2022-08-16
- License: BSD-3-Clause
- URL: https://github.com/janelia-pypi/kicad_bom
- Author: Peter Polidoro
- Email: peter@polidoro.io
- Copyright: 2023 Howard Hughes Medical Institute
- References:
  - https://gitlab.com/kicad/code/kicad
- Dependencies:
  - kicad_netlist_reader
```


<a id="orgf3dbf7d"></a>

# Example Usage


## Python

```python
from kicad_bom import KicadBom
netlist_path = '.'
output_path = 'test/bom'
kb = KicadBom(netlist_path, output_path)

kb.save_all_csv_files()

column_names = ['Item',
                'Quantity',
                'Manufacturer',
                'Manufacturer Part Number',
                'Description',
                'Reference(s)',
                'Package']
format_for_org_table = True
bom = kb.get_bom(column_names, format_for_org_table)
```


<a id="orgdd67935"></a>

# Installation

<https://github.com/janelia-pypi/python_setup>


## GNU/Linux


### Python Code

The Python code in this library may be installed in any number of ways, chose one.

1.  pip

    ```sh
    python3 -m venv ~/venvs/kicad_bom
    source ~/venvs/kicad_bom/bin/activate
    pip install kicad_bom
    ```

2.  guix

    Setup guix-janelia channel:
    
    <https://github.com/guix-janelia/guix-janelia>
    
    ```sh
    guix install python-kicad-bom
    ```


## Windows


### Python Code

The Python code in this library may be installed in any number of ways, chose one.

1.  pip

    ```sh
    python3 -m venv C:\venvs\kicad_bom
    C:\venvs\kicad_bom\Scripts\activate
    pip install kicad_bom
    ```


<a id="orgfcd8cca"></a>

# Development


## Clone Repository

```sh
git clone git@github.com:janelia-pypi/kicad_bom.git
cd kicad_bom
```


## Guix


### Install Guix

[Install Guix](https://guix.gnu.org/manual/en/html_node/Binary-Installation.html)


### Edit metadata.org

```sh
make -f .metadata/Makefile metadata-edits
```


### Tangle metadata.org

```sh
make -f .metadata/Makefile metadata
```


### Develop Python package

```sh
make -f .metadata/Makefile guix-dev-container
exit
```


### Test Python package using ipython shell

```sh
make -f .metadata/Makefile guix-dev-container-ipython
import kicad_bom
exit
```


### Test Python package installation

```sh
make -f .metadata/Makefile guix-container
exit
```


### Upload Python package to pypi

```sh
make -f .metadata/Makefile upload
```


## Docker


### Install Docker Engine

<https://docs.docker.com/engine/>


### Develop Python package

```sh
make -f .metadata/Makefile docker-dev-container
exit
```


### Test Python package using ipython shell

```sh
make -f .metadata/Makefile docker-dev-container-ipython
import kicad_bom
exit
```


### Test Python package installation

```sh
make -f .metadata/Makefile docker-container
exit
```