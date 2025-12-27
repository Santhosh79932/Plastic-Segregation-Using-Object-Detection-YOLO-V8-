import calendar

# Get user input for the month
user_month = int(input("Enter the month (1-12): "))

# Validate user input
if user_month < 1 or user_month > 12:
    print("Invalid month input. Please enter a number between 1 and 12.")
else:
    # Get the current year
    current_year = 2026  # You can modify this if you want to use the current year or get it dynamically

    # Print the calendar for the specified month and year
    print(calendar.month(current_year, user_month))