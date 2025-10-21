# Response-tools for FOXSI-4 <span>&#129418;</span>

Repository to manage response elements, originally for the FOXSI-4 sounding rocket mission and it can be extended.

**Note:** This repository can be extended to any other instrument (e.g., FOXSI-1, -2, and -3) but only currently supports FOXSI-4 use.

## Setting up the code

The code does not live in a place accessible to package managers like `pip` yet so there are a few steps to take to be able to operate the code.

### Downloading the code

The first step will likely be installing the Python code. The repository, [`response-tools`](https://github.com/foxsi/response-tools), is very lightweight and does not require many dependencies. You can either:

- Do the usual to download the repository contents and retain Git version control via
  - `git clone https://github.com/foxsi/response-tools.git`
- Or just download the repository contents as a ZIP folder and extract the contents
  - Click the <span style="color:green">green Code button</span> then select “Download ZIP”

### Python virtual environments

It is still recommended to create a Python virtual environment in your preferred manner to house the response code; however, this is completely your own choice.

I will quickly run through an example of creating a virtual environment using [conda](https://docs.conda.io/projects/conda/en/stable/index.html):

- `conda create -n response-tools-env python==3.12`

We recommend using Python 3.12 just because this has been proven to be stable with the software, feel free to test other versions if you like.

Remember to activate your environment with:

- `conda activate response-tools-env`

You can check you’re working out of your environment by running:

- `which python`
- `which pip`
  
And making sure the environment is in the returned path (I get something like "/Users/kris/miniconda3/envs/response-tools-env/bin/python"). Note the environment name should be in the path.

It might be a good idea to look into ([conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)) virtual environments if you are not familiar, this includes looking into them yourself or getting in touch with someone to help explain. This requires downloading [miniconda](https://docs.anaconda.com/miniconda/install/#quick-command-line-install) (or just conda if you prefer).

### Installing the code

The Python code can then be installed with:

- `pip install -e .`

while in the directory the `response-tools` directory that contains the `setup.py` file.

Any time the code is updated and, say, you pull/download it from Github, make sure to perform the `pip install -e .` line from above again in your environment. Most of the time this is unnecessary but ensures any new changes, updated versions, etc. definitely take effect.

## Getting the response files

The response files live somewhere in the University of Minnesota. A user can either:

- Use their own methods to trek through the data storage themselves and navigate the plethora of different file formats, standards, personal choices; or,
- Use a Python interface developed to download the files.

### Where the data lives

Public access to the FOXSI-4 flight data is provided at the site:

- [https://foxsi.space.umn.edu/data/response/response-components/](https://foxsi.space.umn.edu/data/response/response-components/)

That link contains several subfolders of response data:

- Attenuation data
- Detector response data
- Effective area data
- Quantum efficiency data

Users can also access the data via FTP at `foxsi.space.umn.edu/FOXSI`. There is no username or password required. Once connected to the FTP server, navigate to `data/response/response-components` to access response files.

**Note:** users on the UMN eduroam WiFi network will not be able to access the `foxsi.space.umn.edu/data` site or the FTP server. All other networks tested have been able to access without issue.

### Python interface to pull data

The following will download all the response files to your machine:

```python
import response_tools.io.fetch_response_data as fetch
fetch.foxsi4_download_required(verbose=True)
# stop trying to make "fetch" happen
```

The functions in the package are designed to know where these function are and just use them as expected.

To find where the files are stored in your filesystem, you can use the global package variable, `responseFilePath`:

```python
import response_tools
print(response_tools.responseFilePath)
```

This allows a user to easily find where the response files are for their own purposes.

A user can also inspect if there are any files missing from what is expected in the `responseFilePath` directory. This is done with:

```python
import response_tools.io.fetch_response_data as fetch
missing_files = fetch.foxsi4_list_missing_response_info()
```

Here, `missing_files` is a tuple where the two entries are the files to get and folders to get, respectively. This function is run on import of the `response-tools` package and will warn the user if files are missing.

## Locations of example code

There are a few existing example scripts showing how to use a lot of tools in the repository.

An [example gallery](auto_examples/index) exists.

Original Python example scripts can be found in response-tools [examples](https://github.com/foxsi/response-tools/tree/main/examples) folder.

## The `response-information` directory

This directory contains context information about the response files that can be shared between a lot of different scripts. E.g., the latest versions of the files the code should be using.

The [YAML](https://github.com/foxsi/response-tools/tree/main/response_tools/response-information) file contained in this directory is used to track the latest versions of files to be used and this directory also stores the data files after being downloaded.

Response data files can be downloaded using:

- `response_tools.io.fetch_response_data.foxsi4_download_required` 

```python
import response_tools.io.fetch_response_data as fetch
fetch.foxsi4_download_required(verbose=True) 
```

This directory can be found on your local machine using a global variable in the package:

```python
import response_tools
print(response_tools.responseFilePath)
```

## Contributing to the repository

If you are thinking about contributing to the repository, thank you so much for considering! <span>&#127881;</span>

Any help would be appreciated and can come in the form of contributing code, fixing bugs, or pointing out errors or places for improvement via [Pull Requests](https://github.com/foxsi/response-tools/pulls) and [Issues](https://github.com/foxsi/response-tools/issues).

In order to contribute code, we ask that you first [create your own fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of the repository and then clone that fork to your local machine. Branches of your new fork can be created to develop new features or fix bugs (exciting!). When you are happy with the code in that new branch, [a pull request (PR) can be opened](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) which aims to merge the code in your fork's branch into the `main` `foxsi/response-tools` repository. A lot of discussion can be facilitated in an open PR.

**Note:** We _never_ `push` to this repository directly. If this happens then it can be very difficult for other contributers to understand what changes are being made and how it affects their own PRs. _If the repository is pushed to directly, in order to help track changes and make them visible to other contributers, the repository will be reverted back to it's state before the push and the undone changes will be asked to be proposed via a PR to then be merged._

## Versioning
This software, and the response data files it uses, are versioned with different syntax. If you are interacting with [Response-tools](https://www.github.com/foxsi/response-tools) at a high level, (e.g. [through the Level 3 or Level 2 API](https://foxsi.github.io/response-tools/code.html#api-level-design)), you don't need to worry about individual response file versions.

### Software versioning
The versioning approach for this software package is [semantic versioning](https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning).

This means that we represent the item with one-three digits indicating `major`.`minor`.`patch` changes made.

- `major`: Increment to include breaking changes from previous versions.
  - E.g., the pre-existing code's behaviour is changed and is no longer backwards-compatible.
- `minor`: Increment to include new additions to the software.
  - E.g., code has new tools.
- `patch`: Increment to include all other small changes.
  - E.g., the code has had a couple of small typo or bug fixes.

### File versioning
Response files are versioned using only an integer version number. File versions are updated _any time_ their data content changes (modifications, removals, or additions). The developers of Response-tools keep the available software tools aligned with the available response data. 

Response files may be added as new aspects of the instrument response are understood. Response files may update their version if e.g. improved calibration results are available.