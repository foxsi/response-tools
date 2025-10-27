# Versions and Releases <span>&#129418;</span>

This section of the documentation will provide meta information and track the history on the code and file versions.

In a list of versions, the latest will be at the top and the oldest at the bottom.

Files will be arranged by code version and component type. The same structure as the `response_tools.contextResponseInfo` dictionary will be used.

## Version `1.0.0`

The first complete version of the code. Found via:

```python
import response_tools
print(response_tools.__version__)
```

### Optics

- eff_area_telescope-2-pan_msfc_heritage:
  - `v1`: effective-area-data/FOXSI3_Module_X-7_EA_pan_v1.txt
    - Pan file for the effective areas at energies and off-axis angles when the optics up coincides with Solar North (“horizontal”).
- eff_area_telescope-2-tilt_msfc_heritage:
  - `v1`: effective-area-data/FOXSI3_Module_X-7_EA_tilt_v1.txt
    - Tilt file for the effective areas at energies and off-axis angles when the optics up coincides with Solar North (“vertical”).
- eff_area_telescope-5-pan_msfc_heritage:
  - `v1`: effective-area-data/FOXSI3_Module_X-8_EA_pan_v1.txt
    - Pan file for the effective areas at energies and off-axis angles when the optics up coincides with Solar North (“horizontal”).
- eff_area_telescope-5-tilt_msfc_heritage:
  - `v1`: effective-area-data/FOXSI3_Module_X-8_EA_tilt_v1.txt
    - Tilt file for the effective areas at energies and off-axis angles when the optics up coincides with Solar North (“vertical”).
- eff_area_msfc_hi_res:
  - `v1`: effective-area-data/FOXSI4_Module_MSFC_HiRes_EA_with_models_v1.txt
    - Effective areas at energies for the MSFC High-resolution optic. No off-axis angle information in this version.
- eff_area_measured_nagoya_hxt:
  - `v1`: effective-area-data/nagoya_hxt_onaxis_measurement_v1.txt
    - Effective areas at energies for the Nagoya Hard X-ray optic. No off-axis angle information in this version.
- eff_area_measured_nagoya_sxt:
  - `v1`: effective-area-data/nagoya_sxt_onaxis_measurement_v1.txt
    - Effective areas at energies for the Nagoya Soft X-ray optic. No off-axis angle information in this version.
- eff_area_cmos_mirror0:
  - `v1`: effective-area-data/foxsi4_telescope-0_BASIC_mirror_effective_area_v1.fits
    - CMOS team prepared effective areas at energies for the MSFC X-ray optic. No off-axis angle information in this version.
- eff_area_cmos_mirror1:
  - `v1`: effective-area-data/foxsi4_telescope-1_BASIC_mirror_effective_area_v1.fits
    - CMOS team prepared effective areas at energies for the Nagoya Soft X-ray optic. No off-axis angle information in this version.
- eff_area_cmos_telescope0:
  - `v1`: effective-area-data/foxsi4_telescope-0_BASIC_TELESCOPE_RESPONSE_v1.fits
    - CMOS team prepared full telescope response for telescope 0. No off-axis angle information in this version.
- eff_area_cmos_telescope1:
  - `v1`: effective-area-data/foxsi4_telescope-1_BASIC_TELESCOPE_RESPONSE_v1.fits
    - CMOS team prepared full telescope response for telescope 1. No off-axis angle information in this version.
- eff_area_early_nagoya_sxt:
  - `v1`: effective-area-data/effective-area_raytracing_soft-xray-optic_on-axis_v1.txt
    - Early version of the effective areas at energies for the Nagoya Soft X-ray optic. No off-axis angle information in this version.
- eff_area_early_msfc_hi_res:
  - `v1`: effective-area-data/3Inner_EA_EPDL97_14AA_v1.csv
    - Early version of the effective areas at energies for the MSFC X-ray optic. No off-axis angle information in this version.
- eff_area_modeled_nagoya_hxt:
  - `v1`: effective-area-data/HXR_Nagoya_FOXSI4_v1.arf
    - Nagoya team prepared effective areas at energies for the Nagoya Hard X-ray optic. No off-axis angle information in this version.
- eff_area_modeled_nagoya_sxt:
  - `v1`: effective-area-data/SXR_nocollimator_noobf_v1.arf
    - Nagoya team prepared effective areas at energies for the Nagoya Soft X-ray optic. No off-axis angle information in this version.

### Detectors

- cmos_det_telescope-0_resp:
  - `v1`: detector-response-data/cmos/foxsi4_telescope-0_BASIC_RESPONSE_MATRIX_v1.fits
    - CMOS team prepared detector response matrix for telescope 0.
- cmos_det_telescope-1_resp:
  - `v1`: detector-response-data/cmos/foxsi4_telescope-1_BASIC_RESPONSE_MATRIX_v1.fits
    - CMOS team prepared detector response matrix for telescope 1.
- cdte_det_merged_resp:
  - `v1`: detector-response-data/cdte/merged_v1/
    - CdTe team prepared detector response matrix for depth-of-interaction corrected merged energies.
- cdte_det_pt_resp:
  - `v1`: detector-response-data/cdte/pt_v1/
    - CdTe team prepared detector response matrix for Pt-side energies.

### Attenuation

- att_thermal_blanket:
  - `v1`: attenuation-data/F4_Blanket_transmission_v1.dat
    - Transmissions for the thermal blanket material (MLI blanket).
- att_pixelated:
  - `v1`: attenuation-data/20240607_fosxi4_transmission_v1.csv
    - Transmissions for the pixelated attenuator.
- att_al_mylar:
  - `v1`: attenuation-data/thin_mylar_p3_p5_theoretical_v1.csv
    - Transmissions for the thin aluminized Mylar.
- att_telescope-2_uniform_al_cdte:
  - `v1`: attenuation-data/unif_att_p2_theoretical_v1.csv
    - Transmissions for position 2's uniform, monolithic Al attenuator.
- att_telescope-4_uniform_al_cdte:
  - `v1`: attenuation-data/unif_att_p4_theoretical_v1.csv
    - Transmissions for position 4's uniform, monolithic Al attenuator.
- att_telescope-0_collimator_ratio:
  - `v1`: attenuation-data/foxsi4_telescope-0_BASIC_collimator_aperture_ratio_v1.fits
    - Collimator ratio for telescope 0.
- att_telescope-1_collimator_ratio:
  - `v1`: attenuation-data/foxsi4_telescope-1_BASIC_collimator_aperture_ratio_v1.fits
    - Collimator ratio for telescope 1.
- att_telescope-0_cmos_obfilter:
  - `v1`: attenuation-data/foxsi4_telescope-0_BASIC_optical_blocking_filter_transmittance_v1.fits
    - Transmissions for telescope 0's uniform, monolithic optical blocking filter.
- att_telescope-1_cmos_obfilter:
  - `v1`: attenuation-data/foxsi4_telescope-1_BASIC_optical_blocking_filter_transmittance_v1.fits
    - Transmissions for telescope 1's uniform, monolithic optical blocking filter.
- att_telescope-0_cmos_prefilter:
  - `v1`: attenuation-data/foxsi4_telescope-0_BASIC_attenuation_filter_transmittance_v1.fits
    - Transmissions for telescope 0's uniform, monolithic pre-filter.
- att_telescope-1_cmos_prefilter:
  - `v1`: attenuation-data/foxsi4_telescope-1_BASIC_attenuation_filter_transmittance_v1.fits
    - Transmissions for telescope 1's uniform, monolithic pre-filter.
- att_foxsi4_atmosphere:
  - `v1`: attenuation-data/FOXSI4_atmospheric_transmission_v1.fits
    - Transmissions for atmospheric attenuation during the FOXSI-4 flight.
- att_early_cmos_prefilter:
  - `v1`: attenuation-data/CMOST_Prefilter_transmission_v1.dat
    - Early version transmissions for the CMOS uniform, monolithic pre-filter.

### Quantum efficiency

- qe_cmos_telescope-0:
  - `v1`: quantum-efficiency-data/foxsi4_telescope-0_BASIC_sensor_quantum_efficiency_v1.fits
    - CMOS team prepared detector quantum efficiencies for telescope 0.
- qe_cmos_telescope-1:
  - `v1`: quantum-efficiency-data/foxsi4_telescope-1_BASIC_sensor_quantum_efficiency_v1.fits
    - CMOS team prepared detector quantum efficiencies for telescope 1.
