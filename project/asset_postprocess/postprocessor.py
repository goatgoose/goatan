import json
import sys

class PostProcessor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    @staticmethod
    def _trim_file_names(data):
        frames = data["frames"]
        new_frames = {}
        for image_name, frame in frames.items():
            image_name = image_name.split("_")[-1]
            new_frames[image_name] = frame
        data["frames"] = new_frames

        return data

    def process(self):
        with open(self.input_path, "r") as input_file:
            data = json.load(input_file)

        data = self._trim_file_names(data)
        with open(self.output_path, "w") as output_file:
            json.dump(data, output_file, indent=4)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python postprocessor.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    postprocessor = PostProcessor(input_path, output_path)
    postprocessor.process()
