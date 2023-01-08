# MRI3D

is and application for processing DICOM volume images into more standard 3D formats for further usage. Currently implemented are:

- TIFF - volume is saved as stack of images into a single file
- MagicaVoxel VOX - the volume should be normalized first, so that voxels represent actual cubes

The loaded volume can also be munipulated with:

- Rotation around axis by 90 degrees
- Upsampling twice
- Downsampling twice
- Resampling along one axis to normalize physical texel size

Interpolation is done trilinearly.

\*All of these operations can take some time, especially resampling, even though it's multithreaded and compiled.

## Installation

- Python 3.9.13

Preferably use a virtual environment

```sh
python -m venv .venv
./.venv/Scripts/activate
```

Install dependencies

```sh
pip install -r requirements.txt --use-pep517
```

## Running

```sh
py mri3d
```

## Testing

```sh
pytest
```

## Fixing DICOM files

Convert potentially non-standard files to complient ones (`../fixed/`)

```sh
find . -type d -exec mkdir -p -- ../fixed/{}
find -type f | xargs -L 1 -d '\n' -P 12 -I '{}' dcmconv --replace-wrong-delim --ignore-parse-errors "{}" "../fixed/{}"
```

Generate DICOMDIR file for images in `DICOM`

```sh
dcmmkdir --recurse -Pdv --invent DICOM/
```
