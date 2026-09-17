# Define 3 functions (add,subtract,multiply) that take two numbers as input and return the result

def calculate_sum():
    return num1 + num2

def calculate_difference():
    return num1 - num2

def calculate_product():
    return num1 * num2

# ask user for input to set the variables num1 and num2
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

#call functions and print results
print("Sum: ", calculate_sum())
print("Difference: ", calculate_difference())
print("Product: ", calculate_product())
print("Thank you for using this simple calculator!")
