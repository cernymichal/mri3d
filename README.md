# MRI3D

TODO

Describe a function of developed application, necessary dependencies (e.g. utilize requirements.txt), how to start it, and last but not least how to run tests from CLI.

## Installation

- Python 3.9.13 

```sh
python -m venv .venv
./.venv/Scripts/activate
```

```sh
pip install -r requirements.txt --use-pep517
```

```sh
py mri3d
```

## Fixing DICOM files

converts potentially non-stantdard files to complient ones (`../fixed/`)

```sh
find . -type d -exec mkdir -p -- ../fixed/{}
find -type f | xargs -L 1 -d '\n' -P 12 -I '{}' dcmconv --replace-wrong-delim --ignore-parse-errors "{}" "../fixed/{}"
```

generates dicomdir file for images in `DICOM`

```sh
dcmmkdir --recurse -Pdv --invent DICOM/
```
