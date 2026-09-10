if year < 1582:
    print("Not within the Gregorian calendar period, sorry")
else:
    if year == 2026:
        print("this is the current year!")
    elif year == 2005:
        print("This is the year the author of this script was born!")
    elif year % 4 != 0:
        print("Common Year")
    elif year % 100 != 0:
        print("Leap year")
    elif year % 400 != 0:
        print("Common year")
    else:
        print("Leap year")
