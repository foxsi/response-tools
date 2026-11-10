FOXSI-5 Instrumentation 🦊⚠️
============================

⚠️ **Work In Progress** ⚠️

Details on the make-up of the FOXSI-5 instrument. This page will help a
user decide what response components they want when using the `response
files <https://foxsi.space.umn.edu/data/response/response-components/>`__
and/or `Response-tools <https://foxsi.github.io/response-tools>`__ code.

.. raw:: html

    <style> .colour {color:#e16b27;} </style>

.. role:: colour

Overview
--------

⚠️ **Work In Progress** ⚠️

The FOXSI-5 instrument is composed of seven independent X-ray
telescopes. Each of these seven includes a direct-focusing X-ray optic
module, a focal plane detector, and some attenuation material along the
optical path. The following figure summarizes the focusing optics,
attenuation, and detector elements that comprise each telescope:

FOXSI-5 telescopes
------------------

⚠️ **Work In Progress** ⚠️

If you’d like to do some analysis on FOXSI-5 data, which telescope(s)
should you use? This table may help you make up your mind:

+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| Telescope | Detector           | Optics           | Collimator      | Attenuation                  | Energy range        | Energy resolution | Spatial resolution (FWHM) |
+===========+====================+==================+=================+==============================+=====================+===================+===========================+
| **0**     | CMOS 1             | MSFC 2-shell     | AR = 1:290      | OBF + Prefilter              | 0.8–10 keV          | 0.4 @ 10 keV      | 3.4"                      |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **1**     | CMOS 2             | Nagoya 1-shell   | AR = 1:200      | OBF + Prefilter              | 0.8–10 keV          | 0.4 @ 10 keV      | 1.5"                      |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **2**     | CdTe DSD 4         | MSFC 10-shell    | ---             | :colour:`177.8 µm Al`        | 4–20 keV            | 0.8 @ 14 keV      | 7.2–11.4"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **3**     | CdTe DSD 2         | MSFC 2-shell     | ---             | Pixelated attenuator + Mylar | 4–20 keV            | 0.8 @ 14 keV      | 6.1–10.8"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **4**     | CdTe DSD 3         | Nagoya 1-shell   | ---             | :colour:`50.8 µm Al`         | 4–20 keV            | 0.8 @ 14 keV      | 5.3–10.3"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **5**     | CdTe DSD 1         | MSFC 10-shell    | ---             | Pixelated attenuator + Mylar | 4–20 keV            | 0.8 @ 14 keV      | 7.2–11.4"                 |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+
| **6**     | Timepix            | MSFC 2-shell     | ---             | Mylar                        | 5–20 keV            | 6 @ 60 keV        | 6.9""                     |
+-----------+--------------------+------------------+-----------------+------------------------------+---------------------+-------------------+---------------------------+

Entries :colour:`coloured` indicate a noted change from that component 
used in `FOXSI-4 <https://foxsi.github.io/response-tools/instrument.html#foxsi-4-telescopes>`__.

FOXSI-5 components
------------------

⚠️ **Work In Progress** ⚠️

Each telescope in FOXSI-5 is built from several optical elements. Each
of these elements has its own response. The following sections break
down the response by element type.

Optics
~~~~~~

⚠️ **Work In Progress** ⚠️

Collimators
~~~~~~~~~~~

⚠️ **Work In Progress** ⚠️

Pixelated attenuators
~~~~~~~~~~~~~~~~~~~~~

⚠️ **Work In Progress** ⚠️

Filters and other attenuators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

⚠️ **Work In Progress** ⚠️

Detectors
~~~~~~~~~

⚠️ **Work In Progress** ⚠️

Three types of detectors were flown on FOXSI-5:

#. CMOS soft X-ray detectors in positions 0 and 1,
#. CdTe double-sided strip detectors in positions 2–5,
#. Timepix detector in position 6.

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
   