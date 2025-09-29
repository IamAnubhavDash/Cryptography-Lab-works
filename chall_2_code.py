from Crypto.Cipher import AES

def decrypt_ecb_flag():
    """
    Exploits ECB block reuse to recover the flag from a known header and ciphertext.
    """
    KNOWN_HEADER = (
        "_Have you heard about the quick brown fox which jumps over the lazy dog?\n"
        "__The decimal number system uses the digits 0123456789!\n"
        "___The flag is: "
    )

    try:
        with open("code\ciphertext.bin", "rb") as file:
            data = file.read()
            print(f"[*] Loaded {len(data)} bytes from ciphertext.bin")
    except FileNotFoundError:
        print("Error: ciphertext.bin not found.")
        return

    if len(data) % AES.block_size != 0:
        print("Error: Ciphertext length is not a multiple of AES block size.")
        return

    mapping = {}
    header_len = len(KNOWN_HEADER)
    print(f"[*] Header length: {header_len} characters")

    for idx, char in enumerate(KNOWN_HEADER):
        block = data[idx * AES.block_size : (idx + 1) * AES.block_size]
        if block not in mapping:
            mapping[block] = char

    print(f"[*] Created lookup table with {len(mapping)} unique block-to-char mappings")

    flag_start = header_len * AES.block_size
    decrypted_flag = ""
    unknown_found = False

    print(f"[*] Decrypting flag starting at byte offset {flag_start}...")

    for i in range(flag_start, len(data), AES.block_size):
        block = data[i : i + AES.block_size]
        if block in mapping:
            decrypted_flag += mapping[block]
        else:
            decrypted_flag += "?"
            unknown_found = True

    print(f"[+] Recovered flag: {decrypted_flag}")

    if unknown_found:
        print("[!] Some characters could not be automatically decrypted; infer them manually based on flag format.")

if __name__ == "__main__":
    decrypt_ecb_flag()
