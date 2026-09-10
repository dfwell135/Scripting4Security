blocks = int(input("Enter the number of blocks: "))

#
# Write your code here.
height = 0
layer = 1

while blocks >= layer:
    blocks -= layer
    height = layer
    layer += 1


print("The height of the pyramid:", height)

