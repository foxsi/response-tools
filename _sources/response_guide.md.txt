# What Is a Response? <span>&#129418;</span>

There are many elements to a response to track and there are many important derived products, not to mention the units (uhh! <span>&#128580;</span>). Here we will go into some detail on what different response components mean so it is clearer what a user might actually be working with.

Each telescope component has a response that impacts the photon distribution eventually being read off of the detector (e.g., the optics module, any attenuators, and the detector's own efficiency). All of these elements need to be combined for various scientific spectral analysis investigations. therefore, it is common to discuss the response of the telescope as a whole in terms of its **Ancillary Response Function/File (ARF)**, its **Redistribution Matrix Function/File (RMF)**, and its **Spectral Response Matrix (SRM)**.

It can be difficult to find nice information on these combined elements. It usually comes down to how active individual instrument teams are when uploading their own documentation. [The NICER team is a good example](https://heasarc.gsfc.nasa.gov/docs/nicer/analysis_threads/arf-rmf/#:~:text=Introduction) when documenting their ARF/RMF pipeline for spectral analysis.

## What is an ancillary response function/file (ARF)?

The ARF, at heart, is the combination of an instrument's transmission, effective area, and efficiency information that affect an incoming photon and so is a function of photon energy. For example, it can be easily computed for a simple telescope (only an optic and detector) by multiplying together the optic's effective area and the detector's efficiency. The units of the ARF will, therefore, be cm<sup>2</sup>.

FOXSI-4 contains 7 telescopes (telescopes 0-6), all with different combinations of components. Below is an example of the ARF being created from telescope 2's 1D response components:

- Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015")

![FOXSI-4-telescope2-1D-elements](../response_tools/assets/arf_components_tel2.png "FOXSI-4 telescope 2 ARF make-up.")

These elements are then multiplied together and combined to produce the ARF:

![FOXSI-4-telescope2-1D-ARF](../response_tools/assets/arf_manual_tel2.png "FOXSI-4 telescope 2 ARF.")

Comparing the two figures, a user can see different features in the ARF and might be able to attribute those features to the individual components (e.g., the thermal blanket, the Marshall 10-shell X-7 optics, and/or the Al attenuator). A user can then visually see what photons of different energies experience travelling through the telescope on their way to the detector.

For a coded runthrough of creating an ARF, see the [Create an ARF from scratch](https://foxsi.github.io/response-tools/auto_examples/plot_arf_from_scratch.html#sphx-glr-auto-examples-plot-arf-from-scratch-py) example in the example gallery.

<span style="color:#e16b27">For scientific analysis, a user may also consider effects outside the telescope, such as atmospheric transmission/attenuation, which would be incorporated into the ARF.</span>

## What is a redistribution matrix function/file (RMF)?

The RMF is a matrix that contains the energy redistribution information of the detector, this is the photon-to-count conversion probability. An incoming photon of energy $\epsilon$ can be detected by the telescope's sensor as a count with an energy $\lesssim\epsilon$ (say, $E$) due to scattering, detection efficiency, and energy resolution. Therefore, the energies we are interested in are the ones defined for the RMF creation. I.e., the defined photon energies (input axis) control the energies of the ARF and are also the energies at which to evaluate any photon models; whereas, the defined count bin energies (observable bins or output axis) control the binning of the observed data.

Example RMFs for the CdTe and CMOS can be seen below (see the [Example FOXSI-4 RMFs](https://foxsi.github.io/response-tools/auto_examples/plot_rmf_examples.html#sphx-glr-auto-examples-plot-rmf-examples-py) example in the example gallery) which show the conversion probability of a photon being recorded as detector observable (i.e., either a count with a calibrated energy or DN). The units of a response matrix will be observable/photon (e.g., counts/photon or DN/photon).

![FOXSI-4-telescope0-and-2-2D-RMF](../response_tools/assets/tel0_and_2_rmf.png "FOXSI-4 telescope 0 and 2 RMF.")

The RMF is a single product made of many measurements or simulations and should have a strong response along the diagonal ($\epsilon$=$E$). The RMF will contain features at $E<\epsilon$ produced by different interactions. E.g., the escape peak for each energy will run parallel to the diagonal, elemental fluorescence lines will be vertical at constant $E$, and so on.

## What is a spectral response matrix (SRM)?

The SRM describes the total response of the telescope in question. It takes into account both the ARF and the RMF.

Another commonly used term when discussing instrument responses is DRM (Detector Response Matrix). This is sometimes used as an alternative to SRM in that it encapsulates the full instrument response, while others use it to only represent the detector's response, i.e. the same or similar to the RMF. Given this ambiguity, we will avoid using the term DRM and stick to the more explicitly defined terms listed above.

### How does combining the ARF and RMF into an SRM work?

The SRM is the combination of the ARF and RMF:

```{math}
\textrm{SRM} = \textrm{ARF} \times \textrm{RMF} \quad \textrm{and} \quad \textrm{SRM}_{a, b} = \textrm{ARF}_{a}\cdot\textrm{RMF}_{a,b}
```

where $a$ and $b$ are the elements along the input and output RMF axis, respectively. The units of the SRM will be something like observable photon<sup>-1</sup> cm<sup>2</sup> (e.g., counts photon<sup>-1</sup> cm<sup>2</sup> or DN photon<sup>-1</sup> cm<sup>2</sup>).

Using the SRM, a user can perform a variety of scientific analysis, such as forward fitting and spectral inversion. The SRM describes the link between the incoming photon spectrum and the observed data spectrum.

For example, for forward fitting, if a user has a model photon spectrum ($M_{\textrm{photon}}$) evaluated for the SRM input energy bins then they are able to obtain a model telescope observable spectrum (e.g., a count or DN spectrum):

```{math}
M_{\textrm{observable}} = M_{\textrm{photon}} \# \textrm{SRM} \quad \textrm{and} \quad M_{\textrm{observable}, b} = \sum_{a=0}^{n} M_{\textrm{photon}, a} \cdot \textrm{SRM}_{a, b}
```

where $M_{\textrm{observable}}$ is the model observable spectrum that can be compared to the measured observable spectrum from, say, the flight and $\#$ represents matrix multiplication. A user can make use of spectral fitting software for this analysis:

- [Sunkit-spex](https://github.com/sunpy/sunkit-spex) (`Python`)
- [OSPEX](https://hesperia.gsfc.nasa.gov/ssw/packages/spex/doc/ospex_explanation.htm) (`IDL`)
- [XSPEC](https://heasarc.gsfc.nasa.gov/docs/software/xspec/) (Multiple interfaces)

An example of Telescope 2's ARF, RMF, and SRM is given below to show how the two former elements are combined into the latter (see the [Generating and plotting ARFs, RMFs, and SRMs](https://foxsi.github.io/response-tools/auto_examples/plot_arf_rmf_srm.html#sphx-glr-auto-examples-plot-arf-rmf-srm-py) example in the example gallery).

![FOXSI-4-telescope-2-ARF-RMF-SRM](../response_tools/assets/tel2_arf_rmf_srm.png "FOXSI-4 telescope 2 ARF, RMF, and SRM.")
