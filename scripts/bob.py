# server.py
import pickle
import sys, os, getopt
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

def main():
    bob_socket = CommunicationUtils.create_server_socket(CommunicationUtils.HOST, CommunicationUtils.PORT2)
    rsa = RSA()
    # Generate RSA keys

    connection, address = bob_socket.accept()  
    if connection:
        print(f"Connection established with Eve {address}")
        shared_file = "shared_rsa_params.pkl"
        with open(shared_file, "rb") as file:
                serialized_params = file.read()
            # Deserialize the received params
        received_params = pickle.loads(serialized_params)
        # Extract d, e, and n from received params
        d = received_params.d
        e = received_params.e
        n = received_params.n
        print("Received d:", d)
        print("Received e:", e)
        print("Received n:", n)
        CommunicationUtils.resend_back_corrupt_messages(rsa, connection,d,n)
    else:
        print("No connection accepted.")



if __name__ == "__main__":
    main()