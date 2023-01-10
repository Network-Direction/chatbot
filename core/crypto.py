
"""
Verifies and decrypts Resource Data sent from the Graph API
Used when people write to the chat bot

Usage:
    import this module into the application
    Call rsa_decrypt() to decrypt the symmetric key
    Call validate() to validate the signature
    Call aes_decrypt() to decrypt the message body

Authentication:
    Requires the private key in a PEM file
    This needs to be the key that matches the public key sent to GraphAPI
        (when subscribing to a resource)

Restrictions:
    pip install pycryptodome

To Do:
    None

Author:
    Luke Robertson - January 2023
"""


from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from base64 import b64decode, b64encode
import hmac
import hashlib
import json


PRIV_KEY = 'core\\private.pem'


# Decrypt the encrypted symmetric key
def rsa_decrypt(encrypted_symmetric_key):
    '''
    Decrypts the encrypted session key, as sent from Graph API
    Takes the encrypted key as an argument
    Returns the decrypted key
    '''
    # Read the private key as raw text
    # the 'PRIVATE KEY' tags need to exist in the file
    with open(PRIV_KEY, 'r') as file:
        private_key = file.read()

    # Imports the private key into an 'RsaKey' object
    # Assumes no passphrase is needed
    rsa_key = RSA.import_key(private_key)
    rsa_modulus = rsa_key.n.bit_length() / 8

    # PKCS#1 OAEP is an asymmetric cipher based on RSA with OAEP Padding
    # This can only handle messages smaller than the RSA modulus
    # Create a cipher object that encrypts/decrypts based on the RSA key
    rsa_cipher = PKCS1_OAEP.new(rsa_key)

    # The symmetric key and data from the Graph API is Base64 encoded
    # This decodes both into raw bytes
    # We also need to know how long the symmetric key is
    encrypted_symmetric_key = b64decode(encrypted_symmetric_key)
    symmetric_length = len(encrypted_symmetric_key)

    # The OAEP cipher can only decrypt blocks <= the RSA modulus size
    # If they symmetric key < RSA modulus, just decrypt it
    if symmetric_length < rsa_modulus:
        decrypted_symmetric_key = rsa_cipher.decrypt(encrypted_symmetric_key)

    # If they symmetric key > RSA modulus, break it into blocks,
    #   and decode each individually
    # Each block must be the size of the RSA modulus
    else:
        # The position (block number) in the encrypted string
        offset = 0

        # A list to store decrypted blocks
        blocks = []

        # Loop through each block (256-bit for a 2048-bit RSA key)
        while symmetric_length - offset > 0:
            # Check if there is more than one block remaining
            if symmetric_length - offset > rsa_modulus:
                blocks.append(
                    rsa_cipher.decrypt(
                        encrypted_symmetric_key[offset:offset + rsa_modulus]
                    )
                )

            # If there's just one block left
            else:
                blocks.append(
                    rsa_cipher.decrypt(encrypted_symmetric_key[offset:])
                )

            # Move to the next block (if there is one) and repeat
            offset += rsa_modulus

        # 'blocks' is a list of decrypted blocks
        # Join them into one single value
        decrypted_symmetric_key = b''.join(blocks)

    return decrypted_symmetric_key


# Validate the data is authentic
# Compare our hash to the signature Graph API sent
def validate(decrypted_symmetric_key, data, signature):
    '''
    Validate that the message sent from Graph API has not been tampered with
    Takes the decrypted symmetric key as an argument
    Takes the encrypted date
    Takes the signature from MS GRAPH
    Returns True or False (True = validation successful)
    '''
    # Calculate the HMAC-SHA256 hash digest of the encrypted data
    # Convert the format to a string we can compare
    local_hash = hmac.new(
        decrypted_symmetric_key,
        msg=b64decode(data),
        digestmod=hashlib.sha256
    ).digest()
    local_hash = b64encode(local_hash).decode()

    # Check if the signatures match
    if local_hash == signature:
        return True
    else:
        return False


# Decrypt the body of the message
def aes_decrypt(decrypted_symmetric_key, data):
    '''
    Decrypts the body of the message that Graph API sent
    Takes the decrypted symmetric key
    Returns the decrypted data in JSON form
    '''
    # Decrypt the contents of the message
    # The Initialization Vector (IV) is the first 16-bytes of the symmetric key
    # Cipher is AES, PKCS7, mode is CBC
    iv = decrypted_symmetric_key[:16]
    aes_cipher = AES.new(decrypted_symmetric_key, AES.MODE_CBC, iv=iv)

    # Decrypt the payload (block size is 16)
    # Remove AES padding
    decrypted_payload = unpad(
        aes_cipher.decrypt(
            b64decode(data)
        ),
        block_size=16
    ).decode()
    decrypted_payload = json.loads(decrypted_payload)

    return decrypted_payload
