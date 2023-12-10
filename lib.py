from os import makedirs, path, remove
from zipfile import ZipFile
from requests import Response, get

from utils import measure_time, sep_print_block


def get_filename_from_request(resp: Response) -> str:
    """Extracts filename from response body. Otherwise, returns the file name from the URL."""
    content_disposition = resp.headers.get("Content-Disposition")
    if content_disposition:
        return content_disposition.split("filename=")[-1].strip('"')
    else:
        return resp.url.split("/")[-1]

def unzip_contents(zip_save_dir: str, output_dir: str) -> None:
    """Extracnts CSV files from ZIP archive. After extracting deletes the archive."""
    with ZipFile(zip_save_dir, "r") as zip_ref:
        csv_files = [file for file in zip_ref.namelist() if file.endswith(".csv") and "__MACOSX" not in file]

        if not csv_files:
            print("No CSV files found in the ZIP archive.")
            return

        for csv_file in csv_files:
            zip_ref.extract(csv_file, path=output_dir)
            print(f"Successfully extracted file {csv_file}.")

    remove(zip_save_dir)

@sep_print_block(symbol="=")
@measure_time
def download_resource(url: str, output_dir: str) -> None:
    makedirs(output_dir, exist_ok=True)

    print(f"Downloading resource from {url}...")
    response = get(url, allow_redirects=True)

    if response.status_code != 200:
        print(
            f"An error occured while retrieving resources from {url}. Status code: {response.status_code}."
        )
        return
    content_type = response.headers.get("Content-Type")
    if 'zip' not in content_type:
        print(
            f"Downloading resource from the given URL {url} is not a ZIP archive."
        )
        return
    
    filename = get_filename_from_request(response)

    zip_save_dir = path.join(output_dir, filename)
    with open(zip_save_dir, "wb") as f:
        f.write(response.content)
    print(f"Successfully saved {filename} into {output_dir} directory.")

    unzip_contents(zip_save_dir, output_dir)