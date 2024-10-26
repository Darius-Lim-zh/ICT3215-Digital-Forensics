from PIL import Image
import numpy as np
import textwrap
import os
import glob
import numpy as np


# for PDF interactions
# pip install reportlab --user
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

INPUT_ENCODE_DIR = ".\\encode_in"
OUTPUT_ENCODE_DIR = ".\\encode_out"
INPUT_MEDIA_DIR = ".\\media_in"
OUTPUT_MEDIA_DIR = ".\\media_out"


def divide_string(string, parts):
    return ["".join(chunk) for chunk in np.array_split(list(string), parts)]


def get_file_str(filename):
    """
    Selects a file based on input filepath, returns all text contents of the target file as a str

    Args:
        filename (str): path to target file

    Returns:
        str: String of all text content in target file

    """
    with open(filename,'r') as f:
        b = f.read()
    return b


def reset(val, x):
    '''
    Helper function for encoding functions. Takes in an int, and sets x number of LSB to 0.\n
    E.g. in the case of reset(151,2), 1001 0111 becomes 1001 0100, resulting in 148

    Args:
        val (int): Value to have its LSB modified
        x (int): Number of bits to set to 0

    Returns:
        str: Result int after LSB reset
    

    
    Example: reset(7,1) >> 6
    clarification: 0b111 >> 0b110
    '''
    return (val >> x) << x


def bits_representation(integer, n_bits=8):
    '''
    Takes an integer and returns binary representation\n

    Args:
        integer (int): Int value to convert to binary representation
        n_bits (int): Number of bits to return, default=8

    Returns:
        str: Result int after LSB reset

    '''
    return ''.join(['{0:0',str(n_bits),'b}']).format(integer)


def find_capacity(img, code):
    '''
    Helper function for encoding functions. Takes in np.array form of image (derived via "np.array(Image.open(filename))" ) and secret text, 
    returns size values for both of them

    Args:
        img (ndarray): Object representation of image, derived via "np.array(Image.open(filename))"
        code (int): String to be encoded in image

    Returns:
        medium_size(str): Number of 2-bit LSBs available for encoding
        secret_size(str): Size of string to encode (in 2-bit pairs)

    '''
    # total slots of 2 bits available after deducting 12 slots for size payload
    medium_size = img.size - 12
    # number of 2 bits slots the code needs
    secret_size = (len(code)*8) // 2

    print(f'Total Available space: {medium_size} 2-bit slots')
    print(f'Code size is: {secret_size} 2-bit slots')
    print('space consumed: {:.2f}%'.format((secret_size/medium_size) * 100))

    return medium_size, secret_size


def size_payload_gen(secret_size, n_bits=8):
    '''
    Helper function for encoding functions. Used to derive bit representation of secret string length, 
    to be encoded to image, returning 2 bits at a time

    Args:
        secret_size (int): Size of secret length, derived from find_capacity()
        n_bits (int): Total number of bits to return, default=8

    Returns:
        str: 2 bits at a time of the binary representation, from MSB to LSB
    '''
    # get the binary representation of secret size
    rep = bits_representation(secret_size,n_bits)

    # return 2 bits at a time from msb to lsb
    for index in range(0, len(rep), 2):
        yield rep[index:index+2]


def secret_gen(secret):
    '''
    Takes in a string and returns its binary representation 2 bits at a time
    
    Args:
        secret (str): Secret string

    Returns:
        str: 2 bits at a time of the binary representation, from MSB to LSB

    '''

    # for each character
    for byte in secret:

        # get its binary representation (8 bits)
        bin_rep = bits_representation(ord(byte),8)

        # return 2 bits at a time
        for index in range(0,len(bin_rep),2):
            yield bin_rep[index: index+2]


def encode_capacity(img_copy, sec_size):
    '''
    Encode secret length into image (to tell decoder how far to extract)

    Args:
        img_copy (ndarray): 1D Array of image, output from:\n img_dim = img.shape;img = img.flatten()
        sec_size (int): the size of the secret as an integer derived from find_capacity()

    '''
    
    # get the bits representation of the length(24 bits)
    g = size_payload_gen(sec_size, 24)

    # embed each 2-bit pair to a pixel at a time
    for index, two_bits in enumerate(g):
        
        # reset the least 2 segnificant bits
        img_copy[index] = reset(img_copy[index], 2)
        
        # embed 2 bits carrying info about secret length
        img_copy[index] += int(two_bits,2)


def encode_secret(img_copy, secret_text):
    '''
    Encode secret text into image
    
    Args:
        img_copy (ndarray): 1D Array of image, output from:\n img_dim = img.shape;img = img.flatten()
        secret_text (str): Secret string to be encoded
    '''
    # generate 2 bits pair at a time for each byte in secret
    gen = secret_gen(secret_text)

    # embed to the image
    for index, two_bits in enumerate(gen):
        
        # +12 to prevent overlaping with the size payload bits
        img_copy[index+12] = reset(img_copy[index+12], 2)
        # embed 2 bits of secret data
        img_copy[index+12] += int(two_bits,2)



def encode(input_img_list, output_img_list, secret_file, output_pdf_name):
    '''
    Main function to encode a secret file into all target images, producing a PDF file containing all images.\n
    Returns nothing, but `output_pdf_name` and all encoded images are saved in {OUTPUT_MEDIA_DIR}.

    Args:
        input_img_list (List(str)): List of filepaths to target images for steganography. 
        output_img_list (List(str)): Size of secret length, derived from find_capacity()
        secret_file (str): Name of the secret file to be hidden within the image.
        output_pdf_name (str): Name of the output PDF file that will contain the encoded image.

    '''
    # Read the secret file
    secret = get_file_str(secret_file)

    # divide text of input file into chunks equal to number of input images
    secret_parts = ["".join(chunk) for chunk in np.array_split(list(secret), len(input_img_list))]
    
    output_imageref_list = []
    
    for i, part in enumerate(secret_parts):
        print(f"Part {i}\n{part}")

    for id, img_name in enumerate(input_img_list):
        # Read the image
        img = np.array(Image.open(img_name))
        secret_part = secret_parts[id] + "ddd"      # BUG fix
        # Find the capacity of the image and the size of the secret
        medium_size, secret_size = find_capacity(img, secret_part)
        
        # Check if the secret file is too large for the image
        if secret_size >= medium_size:
            print('Secret file is too large for this image. Please use a larger image.')
            return None
        else:
            if input("Proceed with encoding? (y/n): ").lower() != 'y':
                return None
        
        # Save dimensions of image then flatten it
        img_dim = img.shape
        img = img.flatten()

        # Encode the length of the secret into the image
        encode_capacity(img, secret_size)

        # Encode the secret file into the image
        encode_secret(img, secret_part)

        # Reshape the image back to its original dimensions
        img = img.reshape(img_dim)
    
        # Save the stego image
        im = Image.fromarray(img)
        im.save(output_img_list[id])
        print(f'Done! Stego image "{output_img_list[id]}" has been saved.')

        output_imageref_list.append(im)

    
    # Create a canvas for the PDF
    c = canvas.Canvas(output_pdf_name, pagesize=letter)
    # Get page dimensions
    page_width, page_height = letter

    for im in output_imageref_list:     # iterate all created images to send them to pdf
        # Get image dimensions
        img_width, img_height = im.size

        # Create an ImageReader object from the PIL image
        im_reader = ImageReader(im)

        # Scale the image if it's larger than the page size
        if img_width > page_width or img_height > page_height:
            scale = min(page_width / img_width, page_height / img_height)
            img_width *= scale
            img_height *= scale

        # Calculate position to center the image on the page
        x = (page_width - img_width) / 2
        y = (page_height - img_height) / 2

        # Draw the image onto the PDF canvas
        c.drawImage(im_reader, x, y, width=img_width, height=img_height)

        # Finalize and save the PDF
        c.showPage()
    c.save()
    print(f'Done! PDF "{output_pdf_name}" containing the stego image has been saved.')


def get_filename_list(relative_path, pattern="*"):
    """
    Lists all filenames in the specified relative directory matching the given pattern using the glob module.
    
    Args:
        relative_path (str): The relative path to the directory.
        pattern (str): The glob pattern to match filenames (default is "*" for all files).
    
    Returns:
        List[str]: A list of filenames matching the pattern in the directory.
    """
    try:
        # Construct the search pattern
        search_pattern = os.path.join(relative_path, pattern)
        # print(f"Listing files in directory '{relative_path}' matching pattern '{pattern}':\n")
        
        # Use glob to find files matching the pattern
        filenames = glob.glob(search_pattern)
        
        # Filter out directories
        # filenames = [os.path.basename(file) for file in filenames if os.path.isfile(file)]
        
        # print("Filenames:")
        # for filename in filenames:
        #     print(f"- {filename}")
        
        return filenames
    
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        return []


if __name__ == "__main__":
    # use example
    # encode('.\\media_in\\original.jpg', ".\\media_out\\original.jpg", INPUT_ENCODE_DIR + "\\" +'test_complex_script.py', OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf")
    # add extra newlines or comments (at least 3 chars worth) at end of file to offset bug where last few chars arent ported over

    # use example

    file_ext = ["*.jpg", "*.png", "*.jpeg"]
    input_file_list = []
    for ext in file_ext:
        input_file_list += get_filename_list(INPUT_MEDIA_DIR, pattern=ext)

    output_file_list = [x.replace("media_in", "media_out") for x in input_file_list]
    print("ASSET FILE LISTS")
    print(input_file_list)
    print(output_file_list)
    encode(input_file_list, output_file_list, INPUT_ENCODE_DIR + "\\" +'test_complex_script.py', OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf")




