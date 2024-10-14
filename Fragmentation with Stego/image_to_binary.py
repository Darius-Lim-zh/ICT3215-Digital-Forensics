from PIL import Image
import numpy as np

def print_image_binary_representation(image_path):
    # Open the image and convert it to RGB (or grayscale if you prefer)
    img = Image.open(image_path).convert('RGB')

    # Convert the image to a NumPy array (H, W, 3) for RGB
    img_array = np.array(img)

    # Flatten the image array into a 1D array of pixel values
    flat_img_array = img_array.flatten()

    out = ""
    limit = 20
    c = 0
    # Convert each pixel value to its binary representation
    for pixel in flat_img_array:
        
        binary_pixel = format(pixel, '08b')  # 8-bit binary representation
        out += binary_pixel
        c += 1
        if c >= limit:
            break
    print(out)

# Example usage
image_path = 'original.jpg'  # Replace with the path to your image
# image_path = 'out.png'  # Replace with the path to your image
print_image_binary_representation(image_path)