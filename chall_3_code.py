from pwn import *
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor

HOST = "0.cloud.chals.io"
PORT = 12423

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


def choice1(params: str) -> str:
    recvuntil("parameters: ")
    sendline("1")
    recvuntil("parameters: ")
    sendline(params)
    recvuntil("hex): ")
    ciphertext_hex = recvline().strip()
    return ciphertext_hex

def choice2(params_enc: str) -> (bool, str):
    recvuntil("parameters: ")
    sendline("2")
    recvuntil("hex): ")
    sendline(params_enc)
    resp = recvline().strip()
    if resp == "Invalid parameters! Incorrect padding or Non-ASCII characters detected!":
        recvuntil("hex): ")
        return False, recvline().strip()
    elif resp == "Your parameters have been successfully submitted!":
        return False, ""
    elif resp == "Welcome, admin!":
        recvuntil("flag: ")
        return True, recvline().strip()
        


# ===== YOUR CODE BELOW =====

c_zeros = b'\x00' * 32
c_zeros_hex = c_zeros.hex()
print(f"[*] Crafting payload of 32 null bytes: {c_zeros_hex}")


print("[*] Submitting payload to Choice 2 to trigger padding error and leak key...")

is_admin, p_raw_hex = choice2(c_zeros_hex)
p_raw = bytes.fromhex(p_raw_hex)


p1 = p_raw[0:16]
p2 = p_raw[16:32]


key = strxor(p1, p2)
print(f"[*] Success! Recovered AES key: {key.hex()}")

print("[*] Encrypting 'admin=true' with the recovered key...")
payload = b"admin=true"
payload_padded = pad(payload, AES.block_size)


cipher_encrypt = AES.new(key, AES.MODE_CBC, iv=key)
c_admin_hex = cipher_encrypt.encrypt(payload_padded).hex()
print(f"[*] Crafted admin ciphertext: {c_admin_hex}")

print("[*] Submitting admin ciphertext to get the flag...")
is_admin, flag_enc_hex = choice2(c_admin_hex)

if is_admin:
    print(f"[*] Admin access granted! Got encrypted flag: {flag_enc_hex}")
    
    
    c_flag = bytes.fromhex(flag_enc_hex)
    cipher_decrypt = AES.new(key, AES.MODE_CBC, iv=key)
    flag_padded = cipher_decrypt.decrypt(c_flag)
    flag = unpad(flag_padded, AES.block_size)
    
    print("\n" + "="*40)
    print(f"[+] The final flag is: {flag.decode()}")
    print("="*40 + "\n")
else:
    print("[-] Exploit failed. Could not get the flag.")
    
# ===== YOUR CODE ABOVE =====

# Use the function choice1(params) the send your parameters (str) to the server (Choice 1)
# It returns (given that your input was successfully processed) the ciphertext as a hex-string

#
# Use the function choice2(params_enc) to send your encrypted parameters (hex string) to the server (Choice 2)
# It returns a 2-tuple: the first component being a boolean indicating whether you got admin access (True) or not (False), the second compoennt being the hex-string returned by the server (empty string in the case that the server returns nothing)
    
# ===== YOUR CODE ABOVE =====

try:
    target.close()
except:
    pass
