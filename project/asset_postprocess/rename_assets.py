import sys
import os


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python rename_assets.py <asset dir>")
        sys.exit(1)
    asset_dir = sys.argv[1]

    for asset_file in os.listdir(asset_dir):
        # Should only rename asset files.
        if not os.path.basename(asset_file).startswith("asset_") or not asset_file.endswith(".png"):
            continue

        asset_name = asset_file.split("_")[-1]
        source = os.path.join(asset_dir, asset_file)
        dest = os.path.join(asset_dir, asset_name)
        os.rename(source, dest)
