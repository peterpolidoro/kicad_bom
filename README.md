- [About](#orge095f82)
- [Example Usage](#orgfd5dc88)
- [Installation](#orgf45602e)
- [Development](#org3b00750)

    <!-- This file is generated automatically from metadata -->
    <!-- File edits may be overwritten! -->


<a id="orge095f82"></a>

# About

```markdown
- Python Package Name: kicad_bom
- Description: KiCad Python code for generating bill of materials in multiple formats.
- Python Package Exports: KicadBom, save_all_csv_files
- Version: 5.0.0
- Python Version: 3.9
- Release Date: 2023-03-29
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


<a id="orgfd5dc88"></a>

# Example Usage


## Python

```python

```


## Command Line


### help

```sh

```


### example usage

```sh

```


<a id="orgf45602e"></a>

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


<a id="org3b00750"></a>

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