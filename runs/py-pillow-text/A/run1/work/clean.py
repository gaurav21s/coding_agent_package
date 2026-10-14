from PIL import Image, ImageDraw, ImageFont

def main():
                                              
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

                              
                                                                                 
    font = ImageFont.load_default()
    text = "Hello"
    
                                   
    text_position = (10, 10)
    draw.text(text_position, text, fill="black", font=font)

                                                       
                                                 
    bbox = draw.textbbox(text_position, text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

                                                                             
                                                                                
    resized_image = image.resize((200, 150), resample=Image.Resampling.LANCZOS)

                          
    print(f"Text size: {text_w}x{text_h} pixels")
    print(f"Final image size: {resized_image.size[0]}x{resized_image.size[1]} pixels")

if __name__ == "__main__":
    main()
