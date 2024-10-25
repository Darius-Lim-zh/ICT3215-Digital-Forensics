# This script is used to hide a python script in an image
# scroll down to encode function

from PIL import Image
import numpy as np
import ast
import astor
import os
import random
import importlib
# from fragment import CodeFragmenter
import glob



# for PDF interactions
# pip install reportlab --user
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

INPUT_ENCODE_DIR = ".\\encode_in"
OUTPUT_ENCODE_DIR = ".\\encode_out"
INPUT_MEDIA_DIR = ".\\media_in"
OUTPUT_MEDIA_DIR = ".\\media_out"


def read_secret(filename):
    '''
    take a file name and return its contents
    param filename (string): the name of the file to read
    output (str): the content of the file
    '''
    with open(filename,'r') as f:
        b = f.read()
    return b

def import_image(filename):
    '''
    loads an image and returns a numpy array of the image
    param filename (str): name of the image to be loaded

    output (ndarray): 3D array of the image pixels (RGB)
    '''
    return np.array(Image.open(filename))

def reset(pixel, n_lsb):
    '''
    Takes an integer and set n least significant bits to be 0s
    param pixel (int): the set of bits to be modified. Ex: 255
    param n_lsb (int): number of least significant bits to set as 0s Ex: 2

    output (int): integer representing to byte after resetting n-lsb
    
    Example: reset(7,1) >> 6
    clarification: 0b111 >> 0b110
    '''
    return (pixel >> n_lsb) << n_lsb


def bits_representation(integer, n_bits=8):
    '''
    takes an integer and return its binary representaation
    param integer (int): The integer to be converted to binary
    param n_bits (int): number of total bits to return. Default is 8

    output (str): string which represents the bits of the integer value

    Example: bits_representation(3, 8) >> 00000011
    '''
    return ''.join(['{0:0',str(n_bits),'b}']).format(integer)

def find_capacity(img, code):
    '''
    Takes a 3D image and the secret file and return their size in 2-bit pairs
    param img (ndarray): the 3d array of the image to be used as a medium
    param code (str): the file you want to hide in the medium

    output medium_size(int): the available size to hide data (in 2 bit pair)
    output secret_size(int): the size of the secret file (in 2 bit pair)
    '''
    # total slots of 2 bits available after deducting 12 slots for size payload
    medium_size = img.size - 12
    # number of 2 bits slots the code needs
    secret_size = (len(code)*8) // 2

    print(f'Total Available space: {medium_size} 2-bit slots')
    print(f'Code size is: {secret_size} 2-bit slots')
    print('space consumed: {:.2f}%'.format((secret_size/medium_size) * 100))

    return medium_size, secret_size


def size_payload_gen(secret_size, n_bits_rep=8):
    '''
    Takes a binary representation and returns a pair of 2 bits untill finished
    param secret_size (int): an integer to be converted to binary representation
    param n_bits_rep (int): total number of bits. example 8 means there will be 8 bits in total

    output (str): two bits of the binary representation from the most significant bit to least significant
    '''
    # get the binary representation of secret size
    rep = bits_representation(secret_size,n_bits_rep)

    # return 2 bits at a time from msb to lsb
    for index in range(0, len(rep), 2):
        yield rep[index:index+2]

def secret_gen(secret, n_bits_rep=8):
    '''
    Takes the secret file and return 2 bits at a time until done
    param secret (str): the secret file
    param n_bits_rep (int): total number of bits. example 8 means there will be 8 bits for each character

    output (str): two bits of the binary representation of each character
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
    Encode the length of the secret file to the image (payload has a standard size of 24 bits)
    param img_copy (ndarray): a 1d vector of the image (flattened)
    param sec_size (int): the size of the secret as an integer
    '''
    
    # get the bits representation of the length(24 bits)
    g = size_payload_gen(sec_size, 24)

    # embed each 2-bit pair to a pixel at a time
    for index, two_bits in enumerate(g):
        
        # reset the least 2 segnificant bits
        img_copy[index] = reset(img_copy[index], 2)
        
        # embed 2 bits carrying info about secret length
        img_copy[index] += int(two_bits,2)


def encode_secret(img_copy, secret):
    '''
    Encode the secret file to the image
    param img_copy (ndarray): a 1d vector of the image (flattened)
    param secret (str): the secret file to be encoded into the image
    '''
    # generate 2 bits pair at a time for each byte in secret
    gen = secret_gen(secret)

    # embed to the image
    for index, two_bits in enumerate(gen):
        
        # +12 to prevent overlaping with the size payload bits
        img_copy[index+12] = reset(img_copy[index+12], 2)
        # embed 2 bits of secret data
        img_copy[index+12] += int(two_bits,2)


def encode(images, output_img_names, secret_file, output_pdf_name):
    '''
    Encodes a secret file into multiple images using RGB steganography and embeds those images into a PDF.

    Parameters:
    - images (List[str]): List of image file paths to use as the medium for hiding parts of the secret.
    - output_img_names (List[str]): List of output image file paths to save the encoded images.
    - secret_file (str): Path to the secret file to be hidden within the images.
    - output_pdf_name (str): Path of the output PDF file that will contain the encoded images.

    Output:
    - A list of stego images saved as `output_img_names`.
    - A PDF file saved as `output_pdf_name` containing the encoded images.
    
    Note:
    - Each image should have a corresponding output image file name in `output_img_names`.
    '''
    # Ensure lists have matching lengths
    if len(images) != len(output_img_names):
        print("Error: The number of images and output image names must be equal.")
        return None

    # Read and prepare the secret data
    secret = read_secret(secret_file)
    secret += "ddd"  # Bugfix for last characters truncation
    parts = [secret[i::len(images)] + "ddd" for i in range(len(images))]  # Split into equal parts

    for idx, (img_file, output_img_name) in enumerate(zip(images, output_img_names)):
        # Read the image
        img = import_image(img_file)

        # Calculate the capacity and check against part size
        medium_size, part_size = find_capacity(img, parts[idx])

        if part_size >= medium_size:
            print(f'Secret part {idx+1} is too large for the image: {img_file}. Use larger images.')
            return None

        # Save dimensions of the image and flatten
        img_dim = img.shape
        img = img.flatten()

        # Encode the part length and the part itself into the image
        encode_capacity(img, part_size)
        encode_secret(img, parts[idx])

        # Reshape and save the stego image
        img = img.reshape(img_dim)
        stego_image = Image.fromarray(img)
        stego_image.save(output_img_name)
        print(f'Done! Stego image "{output_img_name}" for part {idx+1} has been saved.')

    # Embed all encoded images into a PDF
    images_for_pdf = [Image.open(img_path) for img_path in output_img_names]
    images_for_pdf[0].save(output_pdf_name, save_all=True, append_images=images_for_pdf[1:])
    print(f'Done! PDF file "{output_pdf_name}" containing encoded images has been saved.')


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
        # filenames = [os.path.basename(file) for file in files if os.path.isfile(file)]
        
        # print("Filenames:")
        # for filename in filenames:
        #     print(f"- {filename}")
        
        return filenames
    
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        return []


if __name__ == "__main__":
    # use example

    file_ext = ["*.jpg", "*.png", "*.jpeg"]
    file_list = []
    for ext in file_ext:
        file_list += get_filename_list(INPUT_MEDIA_DIR, pattern=ext)
    print(file_list)
    # encode('original.jpg', "out.png", 'test_rev_shell.py', "test_out.pdf")


    # # AUTO CODE FRAGMENT TESTING
    # fragmenter = CodeFragmenter()
    # with open("./test_rev_shell.py", 'r') as script:
    #     code = script.read()
    # parsed_code = ast.parse(code)
    # # Apply the transformation
    # transformed_code = fragmenter.visit(parsed_code)

    # # Finalize by adding the new functions at the top
    # transformed_code = fragmenter.finalize(transformed_code)

    # # Convert AST back to code
    # new_code = astor.to_source(transformed_code)
    # print(new_code)
    # with open("./2_ast_out.py", 'w') as fragment_file:
    #     fragment_file.write(f"{new_code}\n\n")


