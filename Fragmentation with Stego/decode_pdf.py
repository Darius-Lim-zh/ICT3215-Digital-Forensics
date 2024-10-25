from PIL import Image
import numpy as np
import fitz  # PyMuPDF
import io


INPUT_ENCODE_DIR = ".\\encode_in"
OUTPUT_ENCODE_DIR = ".\\encode_out"
INPUT_MEDIA_DIR = ".\\media_in"
OUTPUT_MEDIA_DIR = ".\\media_out"


def import_image(filename):
    '''
    loads an image and returns a numpy array of the image
    param filename (str): name of the image to be loaded

    output (ndarray): 3D array of the image pixels (RGB)
    '''
    return np.array(Image.open(filename))


def decode_capacity(img_copy):
    '''
    extract length of secret file from the image
    param img_copy (ndarray): a 1d vector of the image (flattened)
    output (int): the length of the secret file embedded to this image
    '''
    
    # get the 2 lsb from the first 12 pixels (24 bits)
    bin_rep = ''.join([bits_representation(pixel)[-2:] for pixel in img_copy[:12]])
    # return it as an integer
    return int(bin_rep, 2)

def bits_representation(integer, n_bits=8):
    '''
    takes an integer and return its binary representaation
    param integer (int): The integer to be converted to binary
    param n_bits (int): number of total bits to return. Default is 8

    output (str): string which represents the bits of the integer value

    Example: bits_representation(3, 8) >> 00000011
    '''
    return ''.join(['{0:0',str(n_bits),'b}']).format(integer)


def decode_secret(flat_medium, length, run_code):        # KNOWN BUG: will leave out the last 3 chars, idk why
    '''
    Takes the image, length of hidden secret, and the extension of the output file,
    then extracts secret file bits from the image, executes the decoded Python code,
    and writes it to a new file with the specified extension.
    
    Parameters:
    - flat_medium (ndarray): A 1D vector of the image (flattened)
    - length (int): The length of the secret file extracted using decode_capacity
    '''
    # Initialize a string to accumulate the decoded characters
    decoded_code = ""
    
    # Extract 1 byte at a time (2 bits from each of the 4 pixels)
    for pix_idx in range(12, len(flat_medium), 4):
        # Extract the last 2 bits from each of the 4 consecutive pixels
        byte_bits = ''.join([bits_representation(pixel)[-2:] for pixel in flat_medium[pix_idx:pix_idx+4]])
        
        # Convert the 8 bits to a character
        try:
            byte = int(byte_bits, 2)
            char = chr(byte)
        except ValueError as ve:
            print(f"Error converting bits to character at index {pix_idx}: {ve}")
            continue  # Skip invalid bytes
        
        # Accumulate the character to the decoded_code string
        decoded_code += char
        
        # Check if we've reached the specified length
        if (pix_idx + 4) >= length:
            break
    
    # Execute the decoded Python code
    try:
        
        print(decoded_code)

        if run_code:
            print("Executing the decoded Python code...")
            exec(decoded_code, {'__name__': '__main__'})
            print("Execution completed successfully.")
        return decoded_code
        
    except Exception as e:
        print(f"An error occurred while executing the decoded code: {e}")
        return ""



def decode(stego_img, sec_ext, run_code):
    '''
    this is the driver function to decode a secret file from the stego image
    param stego_img(str): name of the stego image to extract secret from
    param sec_ext(str): the extension of the secret file
    output: a secret file with the specified extension
    '''
    # read image and flatten to 1D
    img = import_image(stego_img).flatten()

    # decode secret length from stego image
    secret_size = decode_capacity(img)
    print(f'secret size: {secret_size}')

    # extract secret file from stego image
    decode_secret(img, secret_size, run_code)

    # print(f'Decoding completed, "{name}.{sec_ext}" should be in your directory')


def extract_images_from_pdf(pdf_path):
    """
    Extracts all images from a PDF file and saves them as temporary files in memory.
    
    Parameters:
    - pdf_path (str): Path to the PDF file
    
    Output:
    - List of PIL Image objects extracted from the PDF
    """
    images = []
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Iterate through each page in the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        # Get the images on the page
        images_list = page.get_images(full=True)
        
        # Extract each image
        for img_index, img in enumerate(images_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert the extracted image bytes to a PIL Image object
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
    
    pdf_document.close()
    return images


def decode_images_from_pdf(pdf_path, output_path):
    """
    Retrieves all images from a PDF file, decodes any hidden information in the images,
    and writes the decoded content to a file.
    
    Parameters:
    - pdf_path (str): Path to the PDF file
    - output_path (str): The extension of the secret file to decode
    """
    # Extract all images from the PDF
    images = extract_images_from_pdf(pdf_path)
    
    # Iterate through each image and run the decoding function\
    formed_script = ""
    for idx, img in enumerate(images):
        img_copy = np.array(img).flatten()  # Flatten the image to a 1D array
        secret_size = decode_capacity(img_copy)
        print(f'Decoding image {idx+1}/{len(images)}, secret size: {secret_size}')
        
        # Extract the secret from the image and save it with a unique filename
        formed_script += decode_secret(img_copy, secret_size, False)
        with open(output_path, 'w', encoding="utf-8") as file:
            file.write(formed_script)
            print(f'Decoded content saved at "{output_path}"')



if __name__ == "__main__":
    # use example
    # decode(OUTPUT_MEDIA_DIR + "\\" + 'original.jpg', 'py', False)
    decode_images_from_pdf(OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf", OUTPUT_ENCODE_DIR + "\\" + "secret.py")


