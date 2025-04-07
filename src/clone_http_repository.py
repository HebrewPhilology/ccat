# This script downloads all the folders, subfolders and files from a repository website
# Frédérique Michèle Rey 2025
# v. 1.0

import os
import requests
from bs4 import BeautifulSoup
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL de base
base_url = "https://ccat.sas.upenn.edu/gopher/text/religion/biblical/"
destination_folder = "ccat"
delay = 0  # Delay in seconds between downloads (to avoid being blocked by the server)

def download_files_from_directory(directory_url: str, destination_folder: str) -> None:
    """
    Function to download files from a given directory
    Args:
        directory_url (str): The URL of the directory containing files.
        destination_folder (str): The local folder to save the downloaded files.
    
    Returns:
        None
    """
    try:
        response = requests.get(directory_url, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        # find all files links
        file_links = soup.find_all(
            "a",
            href=lambda href: href and '.' in href.split('/')[-1]
        )
        
        # Créer le répertoire de destination s'il n'existe pas
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Télécharger chaque fichier
        for link in file_links:
            file_url = directory_url + link["href"]
            file_name = os.path.join(destination_folder, link["href"])
            if os.path.exists(file_name):
                print(f"Le fichier {file_name} existe déjà...")
            else:
                print(f"Téléchargement de {file_url} vers {file_name}")
                with requests.get(file_url, verify=False, stream=True) as r:
                    r.raise_for_status()
                    with open(file_name, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                # Attendre 30 secondes avant de télécharger le prochain fichier
                time.sleep(delay)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'accès au répertoire {directory_url}: {e}")


def explore_and_download(base_url: str, current_url: str, destination_folder: str) -> None:
    """
    Recusively explore directories and download files
    Args:
        base_url (str): The base URL of the website.
        current_url (str): The current URL being explored.
        destination_folder (str): The local folder to save the downloaded files.
    Returns:
        None
    """
    try:
        response = requests.get(current_url, verify=False)
        soup = BeautifulSoup(response.content, "html.parser")

        # Télécharger les fichiers dans le répertoire actuel
        download_files_from_directory(current_url, destination_folder)

        # Trouver tous les sous-répertoires
        directory_links = soup.find_all(
            "a", href=lambda href: href and href.endswith("/") and "gopher" not in href
        )

        for link in directory_links:
            subdirectory_url = current_url + link["href"]
            subdirectory_folder = os.path.join(destination_folder, link["href"].strip("/"))

            print(f"Exploration du sous-répertoire {subdirectory_url}")

            # Appel récursif pour explorer le sous-répertoire
            explore_and_download(base_url, subdirectory_url, subdirectory_folder)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'exploration de {current_url}: {e}")

if __name__ == "__main__":
    explore_and_download(base_url, base_url, destination_folder)
    print("Téléchargement terminé.")
