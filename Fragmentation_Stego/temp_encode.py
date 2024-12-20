

# This script is used to hide a python script in an image
# scroll down to encode function

from PIL import Image
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



def encode(img_file, output_img_name, secret_file, output_pdf_name):
    '''
    This is the driver function to encode a secret file into an image and then embed that image into a PDF file.

    Parameters:
    - img_file (str): Name of the image file to be used as a medium to hide the secret.
    - output_img_name (str): Name of the output image file with the secret encoded.
    - secret_file (str): Name of the secret file to be hidden within the image.
    - output_pdf_name (str): Name of the output PDF file that will contain the encoded image.

    Output:
    - A stego image saved as `output_img_name`.
    - A PDF file saved as `output_pdf_name` containing the stego image.

    Note:
    - All file names must include their extensions (e.g., 'file.jpg', 'output.pdf').
    '''
    # Read the secret file
    secret = read_secret(secret_file)
    secret += "ddd"         # quick bugfix, as decode function will lose 3 chars
    # Read the image
    img = import_image(img_file)
    
    # Find the capacity of the image and the size of the secret
    medium_size, secret_size = find_capacity(img, secret)

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
    encode_secret(img, secret)

    # Reshape the image back to its original dimensions
    img = img.reshape(img_dim)
    
    # Save the stego image
    im = Image.fromarray(img)
    im.save(output_img_name)
    print(f'Done! Stego image "{output_img_name}" has been saved.')



    # Create a canvas for the PDF
    c = canvas.Canvas(output_pdf_name, pagesize=letter)

    # Get image dimensions
    img_width, img_height = im.size

    # Create an ImageReader object from the PIL image
    im_reader = ImageReader(im)

    # Get page dimensions
    page_width, page_height = letter

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





if __name__ == "__main__":
    # use example
    encode('.\\media_in\\original.jpg', ".\\media_out\\original.jpg", INPUT_ENCODE_DIR + "\\" +'test_complex_script.py', OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf")
    # add extra newlines or comments (at least 3 chars worth) at end of file to offset bug where last few chars arent ported over






    # use example

    # file_ext = ["*.jpg", "*.png", "*.jpeg"]
    # input_file_list = []
    # for ext in file_ext:
    #     input_file_list += get_filename_list(INPUT_MEDIA_DIR, pattern=ext)

    # output_file_list = [x.replace("media_in", "media_out") for x in input_file_list]
    # # print(input_file_list)
    # # print(output_file_list)
    # encode(input_file_list, output_file_list, INPUT_ENCODE_DIR + "\\" +'test_complex_script.py', OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf")
    # encode(".\\media_in\\original.jpg", ".\\media_out\\original.jpg",  INPUT_ENCODE_DIR + "\\" +'test_complex_script.py', OUTPUT_MEDIA_DIR + "\\" +"test_out.pdf")




