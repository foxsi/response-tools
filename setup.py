import setuptools

setuptools.setup(
    name="response_tools",
    version="1.0.3",
    description="Software used for the FOXSI response files.",
    url="https://github.com/foxsi/response-tools",
    install_requires=[
            "setuptools",
            "numpy",
            "scipy",
            "matplotlib",
            "pyyaml",
            "astropy",
            "pytest",
            "pandas",
            "beautifulsoup4",
            "inquirer",
            "tqdm",
            "requests",
        ],
    packages=setuptools.find_packages(),
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    include_package_data=True,
)
