from PIL import Image, ImageSequence
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def gif_to_pdf(input_path, output_path):
    with Image.open(input_path) as im:
        frames = []
        for frame in ImageSequence.Iterator(im):
            # Convert to RGB as PDF doesn't support RGBA or P with transparency in the same way
            frames.append(frame.convert("RGB"))

        if frames:
            # Save the first frame and append the rest
            frames[0].save(output_path, save_all=True, append_images=frames[1:])
            print(f"Successfully created {output_path} with {len(frames)} pages.")
        else:
            print("No frames found in GIF.")


if __name__ == "__main__":
    gif_to_pdf("us_evolution.gif", "us_evolution.pdf")
