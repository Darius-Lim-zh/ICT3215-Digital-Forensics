from PIL import Image
import numpy as np
import fitz  # PyMuPDF
import io
import sys

import os


def display_usage():
    print("Usage: python decoder_script.py <pdf_file> <output_secret_file>")
    print("Both arguments are required and must be valid file paths.")
    print("\nArguments:")
    print("  <pdf_file>             Path to the PDF file containing the encoded images")
    print(
        "  <output_secret_file>    Path where the extracted secret file will be saved/if run is in outputfile, it will run instead")


def import_image(filename):
    '''
    Loads an image, returns numpy array

    Args:
        filename (str): Filepath to target image.

    Returns:
        ndarray: 3D array of the image pixels (RGB)
    '''
    return np.array(Image.open(filename))


def decode_capacity(img_copy):
    '''
    Extract length of encoded secret data in image

    Args:
        img_copy (ndarray): flattened 1D vector of image

    Returns:
        int: length of encoded secret data in image
    '''

    # get the 2 lsb from the first 12 pixels (24 bits)
    bin_rep = ''.join([bits_representation(pixel)[-2:] for pixel in img_copy[:12]])
    # return it as an integer
    return int(bin_rep, 2)


def bits_representation(integer, n_bits=8):
    '''
    Takes an integer and returns binary representation\n

    Args:
        integer (int): Int value to convert to binary representation
        n_bits (int): Number of bits to return, default=8

    Returns:
        str: Result int after LSB reset

    '''
    return ''.join(['{0:0', str(n_bits), 'b}']).format(integer)


def decode_secret(flat_medium, length, run_code=False):  # KNOWN BUG: will leave out the last 3 chars, idk why
    '''
    Takes the image, secret length, and a bool flag to set whether to immediately execute the decoded content as code.
    Main function to extract secret from all images in target PDF file, from top to bottom of document in that order.
    Extracted content will first be combined before (optional) execution and output to a file

    Args:
        flat_medium (ndarray): A 1D vector of the image (flattened)
        length (int): The length of the secret file extracted using decode_capacity
        run_code (bool): The flag to set whether to immediately execute extracted text as code

    '''
    # Initialize a string to accumulate the decoded characters
    decoded_code = ""

    # Extract 1 byte at a time (2 bits from each of the 4 pixels)
    for pix_idx in range(12, len(flat_medium), 4):
        # Extract the last 2 bits from each of the 4 consecutive pixels
        byte_bits = ''.join([bits_representation(pixel)[-2:] for pixel in flat_medium[pix_idx:pix_idx + 4]])

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

        if run_code:
            print("Executing the decoded Python code...")
            exec(decoded_code, {'__name__': '__main__'})
            print("Execution completed successfully.")
        return decoded_code

    except Exception as e:
        print(f"An error occurred while executing the decoded code: {e}")
        return ""


def extract_images_from_pdf(pdf_path):
    """
    Extracts all images from a PDF file and saves them as temporary files in memory.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        List(str): List of PIL Image objects extracted from the PDF
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


def decode_images_from_pdf(pdf_path, output_path, run=False):
    """

    Main function, retrieves all images from a target PDF file, then outputs all decoded contents from images into target filepath

    Args:
        pdf_path (str): Path to the PDF file
        output_path (str): Path to the directory to put the extracted contents
        run (bool): True false of whether to run the code
    """
    formed_script = ""
    # Extract all images from the PDF
    images = extract_images_from_pdf(pdf_path)

    # Iterate through each image and run the decoding function\
    formed_script = ""
    for idx, img in enumerate(images):
        img_copy = np.array(img).flatten()  # Flatten the image to a 1D array
        secret_size = decode_capacity(img_copy)
        print(f'Decoding image {idx + 1}/{len(images)}, secret size: {secret_size}')

        # Extract the secret from the image and save it with a unique filename
        formed_script += decode_secret(img_copy, secret_size)

    if run:
        exec(formed_script)
    else:
        with open(output_path, 'w', encoding="utf-8") as file:
            file.write(formed_script)
            print(f'Decoded content saved at "{output_path}"')


if __name__ == "__main__":
    # use example

    # Check for the correct number of arguments
    if len(sys.argv) != 3:
        display_usage()
        sys.exit(1)

    # Unpack arguments
    pdf_file_path, output_path = sys.argv[1:3]
    run = False
    if "run" in output_path:
        run = True

    # Verify each argument is a valid path or writable location
    if not os.path.isfile(pdf_file_path):
        print("Error: The specified PDF file does not exist.")
        display_usage()
        sys.exit(1)

    # if not os.path.isfile(output_path):
    #     print("Error: The output directory does not exist.")
    #     display_usage()
    #     sys.exit(1)

    # out_code_path = os.path.join(output_dir, "secret.py")
    print("Target PDF: " + pdf_file_path)
    # print("Decoded file path: " + output_path)
    decode_images_from_pdf(pdf_file_path, output_path, run)

    # python decode.py ./media_out/out.pdf ./encode_out
