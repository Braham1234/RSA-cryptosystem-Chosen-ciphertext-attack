# client.py
import pickle
import sys, os
import random
import threading
import math
from string import ascii_letters, digits
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import RSAUtils
from scripts.utils import CommunicationUtils
IS_NOT_INTERACTIVE = False

def main():
    client_socket = CommunicationUtils.create_server_socket(CommunicationUtils.HOST,CommunicationUtils.PORT1)
    
    shared_file = "shared_rsa_params.pkl"
    rsa = RSA()
    rsa.generate_key(IS_NOT_INTERACTIVE)
    print(rsa.params.d)
    print(rsa.params.e)
    
    # Serialize the rsa.params object
    serialized_params = pickle.dumps(rsa.params)
    
    # Check if the shared file exists
    if not os.path.exists(shared_file):
        print("Shared file does not exist. Creating a new file.")
    
    # Write the serialized params to the shared file (overwriting any existing content)
    with open(shared_file, "wb") as file:
        file.write(serialized_params)
    connection, _ = client_socket.accept()
    if connection:
        print('Connected to EVE')
    else :
        print('Not Connected from EVE')
    
    CommunicationUtils.send_public_key(connection, rsa)

    # original_message = generate_random_message((rsa.key_length - 8) * random.choice(range(1, 11)))
    original_message = input("Please enter your message: ")
    print("Original message at alice is sending to bob user side:\n", original_message, "\n")
    CommunicationUtils.send_encrypted_messages(connection, rsa.params.e, rsa.params.n, rsa.key_length, original_message)
    


if __name__ == "__main__":
    main()