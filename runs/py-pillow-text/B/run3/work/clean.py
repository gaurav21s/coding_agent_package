from PIL import Image, ImageDraw, ImageFont

def main():
                                              
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

                                                    
    text = "Hello"
                        
    font = ImageFont.load_default()
    
                                                        
                                                 
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
                        
    draw.text((0, 0), text, fill="black", font=font)

                                                                             
    resized_image = image.resize((200, 150), resample=Image.Resampling.LANCZOS)

                       
    print(f"Text size: {text_width}x{text_height} pixels")
    print(f"Final image size: {resized_image.size[0]}x{resized_image.size[1]} pixels")

if __name__ == "__main__":
    main()
