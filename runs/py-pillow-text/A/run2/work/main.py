from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. Create an 800x600 RGB image in memory
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    # 2. Draw the text 'Hello'
    # Using default font (load_default() is the standard way to get a basic font)
    font = ImageFont.load_default()
    text = "Hello"
    
    # Position the text at (10, 10)
    text_position = (10, 10)
    draw.text(text_position, text, fill="black", font=font)

    # 3. Measure the pixel width and height of the text
    # textbbox returns (left, top, right, bottom)
    bbox = draw.textbbox(text_position, text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 4. Resize the image to 200x150 with high-quality (Lanczos) downsampling
    # Image.Resampling.LANCZOS is the current standard for high-quality resizing
    resized_image = image.resize((200, 150), resample=Image.Resampling.LANCZOS)

    # 5. Print the results
    print(f"Text size: {text_w}x{text_h} pixels")
    print(f"Final image size: {resized_image.size[0]}x{resized_image.size[1]} pixels")

if __name__ == "__main__":
    main()
