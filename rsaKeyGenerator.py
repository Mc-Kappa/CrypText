import TRNG
from Crypto.PublicKey import RSA

#for preformace mesuring, use def generator()
#def generator(n):
#    global tries
#    output = TRNG.generateStream(n)
#    tries += 0.5
#    if tries%1 == 0 :
#        print(tries)
#    return output
#pass our string packed into object

def genKeys():
    key = RSA.generate(2048,randfunc=TRNG.generateStream)
    private_key = key
    public_key = key.publickey()
    return private_key, public_key

#tries = 0
key1, key2 = genKeys()

private_key = key1.export_key()
public_key = key2.publickey().export_key()

with open('private.pem', 'wb') as f:
  f.write(private_key)
# Wyświetlenie klucza prywatnego i publicznego
print(f'Private key: {private_key}')
print(f'Public key: {public_key}')

print("Private key has been generated")

