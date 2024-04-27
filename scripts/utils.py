import sys, os
import socket
from time import sleep
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from algorithm.rsa import RSA
from algorithm.utils import UserInterfaceUtils
import time
IS_COMMUNICATION_MODE = True

class CommunicationUtils:
    BUFFER_SIZE = 500000
    HOST = "127.0.0.1"
    PORT1 = 9999
    PORT2 = 8020
    @staticmethod
    def create_server_socket(HOST,PORT):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                server.bind((HOST, PORT))
                server.listen(5)
                print(f"Server socket bound to port {PORT}")
                return server
            except OSError as e:
                if e.errno == 10048:  # WinError 10048: Port already in use
                    print(f"Port {PORT} is already in use. Retrying in 1 second...")
                    time.sleep(1)  # Wait for 1 second before retrying
                else:
                    # If it's another OSError, re-raise it
                    raise
    @staticmethod
    def create_client_socket(HOST,PORT):
        UserInterfaceUtils.display_instruction()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        return client
    
    @staticmethod
    def send_public_key(connection, rsa):
        connection.send(str(rsa.params.n).encode("utf8"))
        sleep(0.01)
        connection.send(str(rsa.params.e).encode("utf8"))
        sleep(0.01)
    
    @staticmethod
    def receive_public_key(client):
        n = int(client.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))        
        e = int(client.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
        return n, e
    
    @staticmethod
    def send_encrypted_messages(connection: socket, e, n, key_length, message):
        if message == "":
            connection.send(str(0).encode("utf8"))
            UserInterfaceUtils.display_termination_message("Sender")
            sys.exit(0)
        else:
            connection.send(str(len(message)).encode("utf8"))
        RSA.send_encrypted_message_blocks(connection, message, e, n, key_length, IS_COMMUNICATION_MODE)

    @staticmethod
    def decrypt_received_messages(client, n, d):
        message_length = int(client.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))
        if message_length == 0:
            UserInterfaceUtils.display_termination_message("Receiver")
            sys.exit(0)
        message = ""
        while message_length != 0:
            block_tuples = client.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8").split("\n")[0:-1]
            for block_tuple in block_tuples:
                block = int(block_tuple.split("\t")[0])
                block_size = int(block_tuple.split("\t")[1])
                decrypted_block = RSA.decrypt_message_block(block, block_size, d, n)
                message += decrypted_block
                message_length -= (block_size/8)
        UserInterfaceUtils.display_received_message(message)
        return message
    
    @staticmethod
    def resend_back_corrupt_messages(rsa, connection,d,n):
        received_message = 1
        while received_message != 0:
            received_message = int(connection.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8"))

            print(received_message)
            # print('value of d')
            # print(rsa.params.d)
            received_message_decrypted = pow(received_message, d, n)
            print("corrupted message : ")
            print(received_message_decrypted)
            print('\n')
            connection.send(str(received_message_decrypted).encode("utf8"))

    @staticmethod
    def receive_all_blocks_at_once(connection, message_length):
        block_tuples = []
        total_received_chars = 0
        while total_received_chars < message_length:
            new_tuples = connection.recv(CommunicationUtils.BUFFER_SIZE).decode("utf8").split("\n")[0:-1]
            for t in new_tuples:
                total_received_chars += int(t.split("\t")[1]) // 8
            block_tuples += new_tuples
        return block_tuples