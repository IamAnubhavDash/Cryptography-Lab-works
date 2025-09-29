from pwn import *
from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor

HOST = "0.cloud.chals.io"
PORT = 23369

# Uncomment the 'process' line below when you want to test locally, uncomment the 'remote' line below when you want to execute your exploit on the server
# target = process(["python", "./server.py"])
target = remote(HOST, PORT)

def recvuntil(msg):
    resp = target.recvuntil(msg.encode()).decode()
    print(resp)
    return resp

def sendline(msg):
    print(msg)
    target.sendline(msg.encode())

def recvline():
    resp = target.recvline().decode()
    print(resp)
    return resp

def recvall():
    resp = target.recvall().decode()
    print(resp)
    return resp


def send_to_server(input: str) -> tuple[str, str]:
    recvuntil("$ ")
    sendline(input)
    recvuntil("Encrypted Input (hex): ")
    inp_enc = recvline().strip()
    recvuntil("Encrypted Output (hex): ")
    outp_enc = recvline().strip()
    return (inp_enc, outp_enc)


# ===== YOUR CODE BELOW =====
# Use the send_to_server(input) function to send your input (str) to the server
# It returns a 2-tuple of strings as output: the first component being the encrypted input (hex-string), the second component being the encrypted output (hex-string)
prep_data = "\x00" * 480
_, prep_cipher_hex = send_to_server(prep_data)

_, flag_cipher_hex = send_to_server("!flag")

flag_cipher_bytes = bytes.fromhex(flag_cipher_hex)
prep_cipher_bytes = bytes.fromhex(prep_cipher_hex)

length = len(flag_cipher_bytes)
keystream_slice = prep_cipher_bytes[320:320+length]
recovered_flag = strxor(flag_cipher_bytes, keystream_slice)

print(recovered_flag)

target.close()
