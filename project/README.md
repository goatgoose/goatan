## Asset generation

Assets are taken from photoshop and converted into a spritesheet (assets.png/assets.json) to be used by pixijs.

1. Export all asset layers to pngs. In photoshop: File > Export > Layers To Files. Output the files to ./assets. Prefix filenames with 'asset'. Select 'Visible Layers Only'. Set the file type to PNG-24. 
2. Generate the spritesheet with [TexturePacker](https://www.codeandweb.com/texturepacker). Select 'PixiJS' as the framework. Load all the pngs in ./assets. Set the data and texture file to assets.json/assets.png.
3. Run the postprocessor on the generated json file: `python3 ./asset_postprocess/postprocessor.py assets.json assets.json`
