import json
import os
import sys
import requests
import concurrent.futures


def download_file(url: str, output_dir: str, category: str, title: str):
    """Download a file and save it to the specified directory."""
    category_dir = os.path.join(output_dir, category)
    os.makedirs(category_dir, exist_ok=True)  # Create category directory if it doesn't exist

    file_path = os.path.join(category_dir, f"{title}.scel")

    # Skip download if file already exists
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return

    # Attempt to download the file
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {title} to {category_dir}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")


def load_json_data(file_path: str):
    """Load JSON data and return the parsed content."""
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        sys.exit(1)


def run_download():
    """Run the download process"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dist_dir = os.path.join(root_dir, "dist")
    json_file = os.path.join(dist_dir, "imei-sougou.json")

    if not os.path.exists(json_file):
        print("The JSON file does not exist")
        sys.exit(0)

    data = load_json_data(json_file)

    # Filter valid download items and handle None values for title
    download_items = [
        (
            item["download_url"],
            dist_dir,
            item.get("cate", "default_category"),
            (item.get("title") or "untitled").replace("/", "_"),
        )
        for item in data
        if isinstance(item.get("download_url"), str) and isinstance(item.get("title"), (str, type(None)))
    ]

    # Use threading to speed up downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(download_file, url, output_dir, category, title)
            for url, output_dir, category, title in download_items
        ]
        # Wait for all downloads to complete
        for future in concurrent.futures.as_completed(futures):
            if future.exception():
                print(f"Download error: {future.exception()}")


if __name__ == "__main__":
    run_download()
