import aiohttp
import aiofiles
from zipfile import ZipFile
from os import makedirs, path, remove

async def get_filename_from_request_async(resp: aiohttp.ClientResponse) -> str:
    content_disposition = resp.headers.get("Content-Disposition")
    if content_disposition:
        return content_disposition.split("filename=")[-1].strip('"')
    else:
        return resp.url.parts[-1]

async def unzip_contents_async(zip_save_dir: str, output_dir: str):
    """Extracts CSV files from ZIP archive. After extracting deletes the archive."""
    with ZipFile(zip_save_dir, "r") as zip_ref:
        csv_files = [file for file in zip_ref.namelist() if file.endswith(".csv") and "__MACOSX" not in file]

        if not csv_files:
            print("No CSV files found in the ZIP archive.\n")
            return

        for csv_file in csv_files:
            zip_ref.extract(csv_file, path=output_dir)
            print(f"Successfully extracted file {csv_file}.\n")

    remove(zip_save_dir)

async def download_resource_async(url: str, output_dir: str, session: aiohttp.ClientSession):
    makedirs(output_dir, exist_ok=True)

    print(f"Downloading resource from {url}...\n")
    
    async with session.get(url, allow_redirects=True) as response:
        if response.status != 200:
            print(f"An error occurred while retrieving resources from {url}. Status code: {response.status}.\n")
            return
        content_type = response.headers.get("Content-Type")
        if 'zip' not in content_type:
            print(f"Downloading resource from the given URL {url} is not a ZIP archive.\n")
            return

        filename = await get_filename_from_request_async(response)
        zip_save_dir = path.join(output_dir, filename)

        async with aiofiles.open(zip_save_dir, 'wb') as f:
            await f.write(await response.read())

        print(f"Successfully saved {filename} into {output_dir} directory.\n")
        await unzip_contents_async(zip_save_dir, output_dir)
