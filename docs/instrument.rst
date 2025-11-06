FOXSI-4 Instrumentation 🦊
==========================

Details on the make-up of the FOXSI-4 instrument. This page will help a
user decide what response components they want when using the `response
files <https://foxsi.space.umn.edu/data/response/response-components/>`__
and/or `Response-tools <https://foxsi.github.io/response-tools>`__ code.

Overview
--------

The FOXSI-4 instrument is composed of seven independent X-ray
telescopes. Each of these seven includes a direct-focusing X-ray optic
module, a focal plane detector, and some attenuation material along the
optical path. The following figure summarizes the focusing optics,
attenuation, and detector elements that comprise each telescope:

.. raw:: html
    :file: ../response_tools/assets/foxsi4-telescopes.svg
    

Light enters the top of the figure and is detected at the bottom. The
telescopes are identified by their **position** number (0 through 6).
This nomenclature for telescope positions is used in FOXSI documentation
throughout this package and beyond.

This package provides access to the response for each telescope (columns
in the above diagram). Documentation of the API used to retrieve the 
`ARF <https://foxsi.github.io/response-tools/response_guide.html#what-is-an-ancillary-response-function-file-arf>`__ 
and `RMF <https://foxsi.github.io/response-tools/response_guide.html#what-is-a-redistribution-matrix-function-file-rmf>`__ 
for each telescope is linked in the diagram, along the bottom. 

If desired, you can also access the response for individual components of each telescope
(each box in the above diagram). The links in each box point to API documentation for 
retrieving the components of each telescope's response. 

FOXSI-4 telescopes
------------------

If you’d like to do some analysis on FOXSI-4 data, which telescope(s)
should you use? This table may help you make up your mind:

+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| Telescope | Detector           | Optics           | Collimator      | Attenuation                  | Energy range        | Energy resolution | Spatial resolution (FWHM) |
+===========+====================+==================+=================+==============================+=====================+===================+===========================+
| **0**     | CMOS 1             | MSFC 2-shell     | AR = 1:290      | OBF + Prefilter              | 0.8–10 keV          | 0.4 @ 10 keV      | 3.4"                      |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **1**     | CMOS 2             | Nagoya 1-shell   | AR = 1:200      | OBF + Prefilter              | 0.8–10 keV          | 0.4 @ 10 keV      | 1.5"                      |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **2**     | CdTe DSD 4         | MSFC 10-shell    | ---             |  381 µm Al                   | 4–20 keV            | 0.8 @ 14 keV      | 7.2–11.4"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **3**     | CdTe DSD 2         | MSFC 2-shell     | ---             | Pixelated attenuator + Mylar | 4–20 keV            | 0.8 @ 14 keV      | 6.1–10.8"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **4**     | CdTe DSD 3         | Nagoya 1-shell   | ---             | 127 µm Al                    | 4–20 keV            | 0.8 @ 14 keV      | 5.3–10.3"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **5**     | CdTe DSD 1         | MSFC 10-shell    | ---             | Pixelated attenuator + Mylar | 4–20 keV            | 0.8 @ 14 keV      | 7.2–11.4"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **6**     | Timepix [1]_       | MSFC 2-shell     | ---             | Mylar                        | 5–20 keV            | 6 @ 60 keV        | 6.9""                     |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+

You may have an idea of which FOXSI-4 telescopes you’d like to use for
analysis. To work with per-telescope response products, you can use the
convenient `Level 3
API <https://foxsi.github.io/response-tools/code.html#api-level-design>`__
to obtain response products for your chosen telescope(s).

If you are also interested in working with the response data for
individual components of a telescope (e.g. the position 2 optic
response, or the position 1 detector response), there is a convenient
`Level 2
API <https://foxsi.github.io/response-tools/code.html#api-level-design>`__
available as well! And detail on those components below.

FOXSI-4 components
------------------

Each telescope in FOXSI-4 is built from several optical elements. Each
of these elements has its own response. The following sections break
down the response by element type.

Optics
~~~~~~

Three types of X-ray optics were flown in FOXSI-4: 1. Single shell,
high-resolution optics from Nagoya University; 2. Double shell,
high-resolution optics from MSFC; 3. 10 shell optics from MSFC.

The response of each of the seven optics modules flown was characterized
experimentally in extensive beamline campaigns [2]_ [3]_. Currently,
only effective area information for each optic is included in the
response. Future updates will add vignetting information and PSF for
each optic.

Retrieving the optic response for a particular telescope will return the
unique, measured response for that optic module.

Collimators
~~~~~~~~~~~

The two CMOS, soft X-ray telescopes (positions 0 and 1) include
collimators to eliminate ghost rays [4]_ which would contaminate the
detector field of view. Each collimator has a different open area ratio
and a different aspect ratio [5]_.

Retrieving the collimator response for a particular telescope will
return an estimated open area value.

Pixelated attenuators
~~~~~~~~~~~~~~~~~~~~~

A new attenuator technology, developed for X-ray spectroscopy
applications, was demonstrated on FOXSI-4. These pixelated attenuators
are produced by etching μm-scale holes into a silicon wafer using
conventional microfabrication methods. The hole pitch, radius, and depth
are tuned to achieve the desired transmission response.

Traditional, monolithic attenuators are used in solar hard X-ray
spectroscopy to remove the excess of soft X-ray photons produced in
flares and avoid saturating detectors with soft X-ray photons. But
monolithic attenuators do this so effectively that there is little soft
X-ray flux left to measure. Pixelated attenuators allow for a tuned
transmission response—reducing the soft X-ray flux from a flare without
eliminating it completely.

Two such pixelated attenuators were flown on FOXSI-4, in front of CdTe
DSD detectors (in positions 3 and 5). Both were characterized in
post-flight beamline tests, and their measured responses were found to
match the modeled prediction very well.

Retrieving the pixelated attenuator response for a telescope will return
a modeled transmission curve.

Filters and other attenuators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

X-ray flux is attenuated along each telescope's optical path by a variety of monolithic filters:

* Thin, metalized foil filters in the CMOS detectors' optical paths. 
    These are used to prevent visible light from contaminating the detector. These are referred to as the OBFs (for optical-blocking filter) and prefilters.

* Aluminized Mylar filters in front of the position 3 and 5 CdTe detectors. 
    These have have a small impact on the transmission for telescopes 3 and 5, they are included primarily to protect the detector surface during integration.

* Thin aluminum filters in front of the position 2 and 4 CdTe detectors. 
    These are included to bring the observed count rate into an acceptable range for the CdTe detectors.

* Multilayer insulation (MLI) blankets in front of the position 2–6 optics. 
    These blankets shield the optic modules from intense infrared radiation and heating; they transmit X-rays well.

..    A sample of this blanket material was measured in the lab post-flight. Its transmission was consistent with models, the API in this package reports the modeled value.

Detectors
~~~~~~~~~

Three types of detectors were flown on FOXSI-4:

#. CMOS soft X-ray detectors in positions 0 and 1,
#. CdTe double-sided strip detectors in positions 2–5,
#. Timepix detector in position 6 [1]_.

The following table summarizes the characteristics of each detector:

+-----------+---------------+-----------------------+-----------+
| Detector  | Energy range  | Energy resolution     | Pitch     |
+===========+===============+=======================+===========+
| CMOS      | 0.8–10 keV    | 0.4 @ 10 keV          | 11 µm     |
+-----------+---------------+-----------------------+-----------+
| CdTe      | 4–20 keV      | 0.8 @ 14 keV          | 60–100 µm |
+-----------+---------------+-----------------------+-----------+
| Timepix   |6–20 keV       | 6 @ 60 keV            | 55 µm     |
+-----------+---------------+-----------------------+-----------+

Prior to the flight, all detectors underwent calibration campaigns 
involving sealed radioactive sources [6]_ and beamline testing [7]_. 

For the CMOS detectors, the response information made available 
through this package was constructed from experimental data taken 
with a representative detector. The detector used to construct the 
response was not flown on FOXSI-4; the detector response is applied 
to the CMOS detectors in positions 0 and 1 identically.

For the CdTe detectors, the response information available through
this package was constructed from experimental data taken with each
specific detector, in combination with GEANT4 simulation. The response 
for CdTe1–CdTe4 is unique to that detector.



.. [1]
   No flight data from Timepix/position 6 is available.

.. [2]
   See Ampuku et al. 2024, DOI: 10.1117/12.3018109

.. [3]
   See Baumgartner et al. 2023, DOI: 10.1117/12.2680486

.. [4]
   See Buitrago-Casas et al. 2020, DOI: 10.1117/12.2561578

.. [5]
   See Sato et al. 2024, DOI: 10.1117/12.3018219

.. [6]
   See Minami et al. 2024, DOI: 10.1117/12.3018742   

.. [7]
   See Shimizu et al. 2024, DOI: 10.1117/12.3017009
   
