"""
Script to download data from FOXSI server.
"""

import os, cmd, sys
import pprint
# from pathlib import PureWindowsPath, PurePosixPath

from bs4 import BeautifulSoup
from enum import Enum
import inquirer
import requests
from tqdm import tqdm
import urllib.request
from urllib.parse import urljoin

from response_tools.io.load_yaml import load_response_context
from response_tools import responseFilePath

local_prefix = 'response-information'

ignore_urls = ['@eaDir/']

DEBUG = True

def print_green(txt:str):
    print('\033[92m' + txt + '\033[0m')
def print_red(txt:str):
    print('\033[91m' + txt + '\033[0m')

class DownloadType(Enum):
    latest = 1
    historical = 2
    component = 3
    telescope = 4
    file = 5



class DownloadPrompt:
    def __init__(self):
        self.remote = "http://foxsi.space.umn.edu/data/response/response-components/"
        self.local_prefix = 'response-information'
        self.start_prompt = [
            inquirer.List(
                "query",
                message="Which data products would you like to download?",
                choices=[
                    ("Get all latest products",                 DownloadType.latest),
                    ("Get all historical products",             DownloadType.historical),
                    ("Get specific response components",        DownloadType.component),
                    ("Get response components for telescope",   DownloadType.telescope),
                    ("Get specific file",                       DownloadType.file)
                ]
            )
        ]
        self.theme = inquirer.themes.load_theme_from_dict({
            "Question": {
                "mark_color": "blue",
                "brackets_color": "normal"
            },
            "List":{
                "selection_color": "bold_green",
                "selection_cursor": ">"
            }
        })
        self.prompt_machine = {
            DownloadType.latest:        self._fetch_latest,
            DownloadType.historical:    self._fetch_historical,
            DownloadType.component:     self._prompt_component,
            DownloadType.telescope:     self._prompt_telecope,
            DownloadType.file:          self._prompt_file
        }

        answers = inquirer.prompt(self.start_prompt, theme=self.theme)

        self._handle_prompt(answers["query"])

    def _handle_prompt(self, reply:DownloadType):
        if reply in self.prompt_machine.keys():
            self.prompt_machine[reply]()
        else:
            raise KeyError("Unimplemented user selection: " + reply)

    def _fetch_latest(self):
        print("latest")
    def _fetch_historical(self):
        print("historical")
    def _prompt_component(self):
        component_prompt = [
            inquirer.Checkbox(
                "component",
                message="Which response component(s) would you like to download?",
                choices=["detector response", "attenuation", "effective area", "quantum efficiency"]
            )
        ]
        answers = inquirer.prompt(component_prompt, theme=self.theme)


    def _prompt_telecope(self):
        telescope_prompt = [
            inquirer.Checkbox(
                "telescope",
                message="Which telescope's products would you like to download?",
                choices=[
                    ("P0 - CMOS detector,    2-shell optic", 0),
                    ("P1 - CMOS detector,    1-shell optic", 1),
                    ("P2 - CdTe detector,   10-shell optic", 2),
                    ("P3 - CdTe detector,    2-shell optic", 3),
                    ("P4 - CdTe detector,    1-shell optic", 4),
                    ("P5 - CdTe detector,   10-shell optic", 5),
                    ("P6 - Timepix detector, 2-shell optic", 6)
                ]
            )
        ]
        answers = inquirer.prompt(telescope_prompt, theme=self.theme)

    def _prompt_file(self):
        file_prompt = [
            inquirer.Text(
                "file",
                message="Provide the URL to download"
            )
        ]
        answers = inquirer.prompt(file_prompt, theme=self.theme)
        print(answers["file"])



def green_str(text:str):
    return "\033[92m" + text + "\033[0m"
        
def foxsi4_list_missing_response_info():
    """Check which response files need downloading, according to 
    ``response-information/info.yaml``.
    
    Look at all the required files in ``info.yaml``, and see which of them are not 
    already on the local disk.
    
    .. note:: Folders will always be flagged for download.
        Some response products are just identified by their folder on the server. 
        There's no knowing if their contents are already downloaded until we go talk to 
        the server (which this function does not do).
    
    Returns
    -------
    A tuple describing two items: ``files_to_get`` and ``folders_to_get``.
    
    ``files_to_get`` is a ``dict`` of each file that should be downloaded from the remote server. The keys in this dictionary are the file names from the ``info.yaml`` file. The value for that key is another ``dict``, which contains the remote server path to the file (under the "remote" key) and the local disk path to save the file (under the "local" key). Like this:
    
        .. code:: python
            
            files_to_get["a_response_file_name"] == {
                "remote": "http://foxsi.space.umn.edu/data/response/response-components/attenuation-data/a_response_file.fits",
                "local":  "response-tools/response_tools/response-information/attenuation-data/a_response_file.fits"
            }

    ``folders_to_get`` is a ``dict`` of each folder that should be downloaded from the remote server. The keys in this dictionary are the folder names from the ``info.yaml`` file. The value for that key is another ``dict``, which contains the remote server path to the folder (under the "remote" key) and the local disk path to save the folder (under the "local" key). Like this:
    
        .. code:: python
            
            folders_to_get["a_response_folder_name/"] == {
                "remote": "http://foxsi.space.umn.edu/data/response/response-components/attenuation-data/a_response_folder/",
                "local":  "response-tools/response_tools/response-information/attenuation-data/a_response_folder/"
            }
    """
    req = load_response_context()
    server_url = req["remote_server"]
    # for urllib.parse.urljoin to work correctly, server path prefix must end in `/`:
    if server_url[-1] != "/":
        server_url += "/"
    local_info_dir = os.path.abspath(responseFilePath)
    files_to_get = {}
    folders_to_get = {}
    for comp_name in req["files"].keys():
        for ftitle, fname in req["files"][comp_name].items():
            path,ext = os.path.splitext(fname)
            if not ext and path[-1] == '/':
                # this is a folder.
                # always add folders to folders_to_get. No way to know if they're full until we read the server.
                
                folders_to_get[ftitle] = {
                    "remote": urljoin(server_url, fname), 
                    "local": os.path.join(local_info_dir, fname)
                }
                # folders_to_get[urljoin(server_url, fname)] = os.path.join(local_info_dir, fname)
            else:
                # this is a file.
                # check if it is on the disk already.
                dest_path = os.path.join(local_info_dir, fname)
                if not os.path.exists(dest_path):
                    files_to_get[ftitle] = {
                        "remote": urljoin(server_url, fname),
                        "local": os.path.join(local_info_dir, fname)
                    }
                    # files_to_get[urljoin(server_url, fname)] = os.path.join(local_info_dir, fname)
    return files_to_get, folders_to_get
    
def foxsi4_download_required(replace_existing=False, verbose=False):
    """Download all response component files specified in ``response-information/info.yaml``.

        Download data products from a remote server to the local filesystem. Retrieves 
        server URL and all local paths for saving data from a config file:
        ``response-tools/response-information/info.yaml``. All downloaded response data will 
        be saved under ``response-tools/response-information``.

        Parameters
        ----------
        replace_existing : ``bool``
            Whether to replace local files with newer versions, if newer versions are
            downloaded. Currently throws ``NotImplementedError``.

        verbose : ``bool``
            Toggle for printing verbosely. If ``True``, download progress indicators and
            filenames are displayed. If ``False``, nothing is printed at all.

        Returns
        -------
        downloaded : ``dict``
            A dict of downloaded data. Keys are the same file identifiers from the YAML
            source. Values are the absolute paths on the local filesystem to the downloaded
            file. Files which were already existed in the local filesystem (required no
            downloaded) are not included in the return value.
    """

    if replace_existing == True:
        raise NotImplementedError("No support yet for replacement of old file versions.")


    def verbose_print(*something):
        if verbose:
            print(*something)
            
    req = load_response_context()
    server_url = req["remote_server"]

    # # for urllib.parse.urljoin to work correctly, server path prefix must end in `/`:
    if server_url[-1] != "/":
        server_url += "/"

    # directory on local filesystem for saving data:
    local_info_dir = os.path.abspath(responseFilePath)
    verbose_print("Retrieving response products from:", green_str(server_url))
    verbose_print("Saving response products to:", green_str(local_info_dir))

    files_to_get, folders_to_get = foxsi4_list_missing_response_info()
    
    downloaded:dict = {}   
    if not files_to_get and not folders_to_get:
        verbose_print("Found nothing new to download")
    else:
        verbose_print("Retrieving files...")
        for ftitle, finfo in tqdm(files_to_get.items(), disable=not verbose):
            remote_path = finfo["remote"]
            local_path = finfo["local"]
            try:
                # create the folders along the save path, if needed
                os.makedirs(os.path.dirname(local_path))
            except FileExistsError:
                pass
                
            fname, head = urllib.request.urlretrieve(remote_path, local_path)
            green_name = os.path.basename(fname)
            downloaded[ftitle] = fname
            if verbose:
                tqdm.write("Downloaded " + green_str(green_name))
        for ftitle, finfo in folders_to_get.items():
            remote_path = finfo["remote"]
            local_path = finfo["local"]
            try:
                # create the folders along the save path, if needed
                os.makedirs(os.path.dirname(local_path))
            except FileExistsError:
                pass
                
            # get the contents of the folder
            page = requests.get(remote_path, timeout=10).text
            soup = BeautifulSoup(page, 'html.parser')
            # make sure we extract all the hrefs then check the link has a "." in it for an extension
            linked_files = [node.get('href') for node in soup.find_all('a') if ("." in node.get('href'))]
            # just download the folder contents
            total_to_get = 0
            for link in tqdm(linked_files, disable=not verbose):
                if os.path.exists(os.path.join(local_path, link)):
                    continue
                else:
                    total_to_get += 1
                    urllib.request.urlretrieve(remote_path+link, os.path.join(local_path, link))
                    green_name = link
                    if verbose:
                        tqdm.write("Downloaded " + green_str(green_name))
            if total_to_get == 0:
                verbose_print("Found nothing new to download under", remote_path)
            else:
                downloaded[ftitle] = local_path
            
    return downloaded

if __name__ == "__main__":
    downloaded = foxsi4_download_required(verbose=True)