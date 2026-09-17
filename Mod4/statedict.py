#Create a program that will reference the state.csv file that will read the file and abbreviate the state names to their two-letter postal cod. The program should create a dictionary where the keys are the full state names and the values are the corresponding two-letter postal codes. Finally, the program should print out the dictionary.

import csv

#Open the state.csv file and read its contents while asking the user for a state to abbreviate
def create_state_dict():
    state_dict = {}
    with open('Mod4/states.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            full_state_name = row[0]
            postal_code = row[1]
            state_dict[full_state_name] = postal_code
    return state_dict
#Ask the user for a state name and print the corresponding postal code
def get_postal_code(state_dict):
    state_name = input("Enter the full name of a state to get its postal code: ")
    postal_code = state_dict.get(state_name)
    if postal_code:
        print(f"The postal code for {state_name} is {postal_code}.")
    else:
        print(f"{state_name} is not found in the dictionary.")

# Create the state dictionary
state_dict = create_state_dict()

# Print the dictionary
print(state_dict)

# Ask the user for a state name and print the corresponding postal code
get_postal_code(state_dict)
