from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. Create an 800x600 RGB image in memory
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # 2. Draw the text 'Hello' with the default font
    text = "Hello"
    # Using default font
    font = ImageFont.load_default()
    
    # 3. Measure the pixel width and height of that text
    # textbbox returns (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Draw text at (0,0)
    draw.text((0, 0), text, fill="black", font=font)

    # 4. Resize the image to 200x150 with high-quality (Lanczos) downsampling
    resized_image = image.resize((200, 150), resample=Image.Resampling.LANCZOS)

    # Print the results
    print(f"Text size: {text_width}x{text_height} pixels")
    print(f"Final image size: {resized_image.size[0]}x{resized_image.size[1]} pixels")

if __name__ == "__main__":
    main()
