import hashlib
import random
import string

#function to generate a new strong password
def generate_password(length=14):
    #define the character set for the password
    characters = string.ascii_letters + string.digits + string.punctuation
    #generate a random password using the character set
    password = ''.join(random.choice(characters) for i in range(length))
    return password
# print(generate_password())

#Path to rockyou.txt file
rockyou_path = 'rockyou.txt'

#prompt user to enter a password
user_password = input("Enter your password to check if it's in the compromised list: ")

#Hash to user password using SHA-1
found = False
try:
    with open(rockyou_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            if user_password.strip() == line.strip():
                found = True
                break
except FileNotFoundError:
    print(f"Error: the file '{rockyou_path}' was not found.")
    exit(1)

#warn user if password is found on compromised list.
if found:
    print("Warning: Your password is in the compromised list!")
    new_password = generate_password()
    print(f"Here is a new strong password you can use: {new_password}")
else:
    print("\nGood news!\n Your password is not in the compromised list.\n")