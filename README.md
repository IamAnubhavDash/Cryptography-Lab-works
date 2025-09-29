# Cryptography-Lab-works
two lab works that contains codes and writeups for various problems including finding vulnerabilities and capturing the flag.

Challenge 1: You’ve been provided a file ciphertext.bin which contains an encryption of the flag encrypted
using aes-128-cbc with the key given in key.hex and the IV given in iv.hex. Use your knowledge
of openssl to decrypt the ciphertext and retrieve the flag!
-
-----SOLUTION-----
This first one was a pretty standard welcome challenge. We were given a ciphertext file, a key,
and an IV, and told to decrypt it. The algorithm was AES-128-CBC, so the plan was to just
fire up OpenSSL and plug everything in.
Here’s the one-liner that did the trick:
openssl enc -d -aes-128-cbc -in ciphertext.bin \
-out flag.txt -K $(cat key.hex) -iv $(cat iv.hex)
Breaking it down:
• -d: Tells OpenSSL we’re decrypting.
• -aes-128-cbc: The specific algorithm to use.
• -K and -iv: These flags are for the Key and IV. We just ‘cat‘ the hex files directly into
the command.
• -in and -out: Specifies the input and output files.
Running that command spits out the flag into flag.txt. Done and done!

Challenge 2: The ECB (Electronic Code Book) mode of encryption is a “bad” mode of encryption because it
always maps the same block of plaintext to the same block of ciphertext. Thus, if you have a long
message such that the same block repeats twice in the plaintext, the same block would repeat in
the exact same position in the ciphertext too. This leaks information about the plaintext.
As an example of the amount of information this leak can reveal, here’s a picture of what happens
when you encrypt the famous Tux penguin using ECB mode:
In this challenge, you will exploit this redundancy of ECB to obtain the flag. The encryption
code is present in encryptor.py and the resultant ciphertext is in ciphertext.bin.
-
-----SOLUTION-----
Ah, the classic ECB attack! ECB mode is famously bad because the same chunk of plaintext
always turns into the same chunk of ciphertext. It leaves patterns all over the place, which
makes it super insecure.
The trick to this challenge was that the encrypted file started with a long header message that
we already knew. This lets us pull off a known-plaintext attack:
1. Build a Cheat Sheet: We chopped the ciphertext into 16-byte blocks. For the part of the
file where we knew the original text (the header), we created a map: ‘encryptedblock− >
originalcharacter‘.
1. Decode the Flag: Once the map was built, we just ran it against the rest of the file (the
part with the flag). Every time we saw a block that was in our map, we knew what the
original character was.
By matching the blocks, we could piece the flag together, character by character.


Challenge 3: Some people believe that since the key is already being randomly generated, the key can also be
repurposed as the IV as long as the IV is not being revealed. This is a rookie mistake and in
general, a very bad idea.
In this challenge, you are going to submit “parameters” (each message is a string of the form
key1 =value1 &key2 =value2 &· · · &key-n=value-n) to a server. These messages are supposed to comprise of normal low-ASCII characters and should not contain the string admin=true as a substring.
CS 409M Page 1 of 3 Lab 2
You will receive the encryption of your messages. The server also lets you send encrypted parameters to it, which it will decrypt internally; while the server does not send you the decryption,
it will throw an error if it finds offending invalid characters in the decrypted text. If you can
somehow send the server an encrypted parameter string which decrypts to a normal string which
has admin=true as a substring, you will receive the encryption of the flag in return.
Abuse the fact that the server repurposes the key as the IV to craft an intelligent payload which
allows you to recover the flag. Good luck on your mission!
The following diagrams could be of help to you (here “encryption” and ”decryption” refer to the
forward and reverse applications of the block cipher):
-
---Solution--
Okay, this one was sneaky. The server made a huge rookie mistake: it used the same secret
value for both the AES key and the IV in CBC mode. This totally breaks the encryption and
lets you actually steal the key.
The attack was a two-step process:
Part 1: Stealing the Key
The goal was to trick the server into leaking its own key. We did this by sending it a carefully
crafted piece of garbage ciphertext—specifically, 32 bytes of all zeros.
Because of how CBC decryption math works (and the key-as-IV flaw), when the server tried
to decrypt our junk and hit a padding error, the error message it sent back contained the raw
decrypted blocks. A little XOR magic on those two blocks (P1 ⊕ P2) cancelled everything out
and left us with the original key. Heist complete!
Part 2: Forging an Admin Token
Once we had the key, the rest was easy. We just played pretend-server and encrypted the
message "admin=true" ourselves. The important part was to make the same mistake the server
did by using the stolen key as the IV.
We sent our freshly forged ciphertext to the server. It decrypted it, saw "admin=true", and
happily handed over the encrypted flag. Since we already had the key, decrypting the flag was
the final, simple step.


Challenge 4: The CTR (CounTeR) mode of encryption is commonly used to convert a block cipher into
an equivalent stream cipher. Do take a look at https://pycryptodome.readthedocs.io/en/
latest/src/cipher/classic.html#ctr-mode to understand how to use the PyCryptodome library for CTR encryption mode (along with an explanation of how CTR mode works if you need
a refresher).
In this challenge, you will interact with a server which essentially acts as an echo server - it outputs
back to you exactly what you input to it – except that the response is encrypted. However, if you
input !flag to it, the server instead outputs the flag to you – again, encrypted. The encryption is
done using CTR mode, using a key you don’t know. But you suspect that the implementation of
the CTR mode encryption in the server has some vulnerability. Refer to the server.py template
file for details on the workings of the server, identify the vulnerability and exploit it to retrieve
the flag.
-
-----SOLUTION-----
The last one was a CTR mode challenge. CTR mode turns a block cipher into a stream cipher,
and its #1, most important rule is: NEVER reuse a nonce!
Guess what this server did? It reused the same nonce for every single connection.
Part 1: Stealing the Keystream
CTR works by generating a secret ”keystream” and XORing your text with it. The server was
an ”echo” server, meaning it would encrypt and send back whatever we sent it.
So, we sent it a long string of null bytes (\x00). When you XOR something with zeros, you
just get the original thing back. So the server’s response (zeros ⊕ keystream) was literally the
keystream itself. We just saved it to a variable.
Part 2: Decrypting the Flag
With the secret keystream in hand, we just had to ask the server for the flag by sending "!flag".
It replied with the encrypted flag, which was just flag ⊕ keystream.
All we had to do was take the server’s response and XOR it with the keystream we already
stole. The two keystreams cancelled each other out, and the flag just popped out in plaintext.
Easy peasy.

