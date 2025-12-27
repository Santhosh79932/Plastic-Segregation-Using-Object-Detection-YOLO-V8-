import os
import portalocker  # For file locking

def fileincreamnet():
    # Create the file if it doesn't exist with initial value 0
    if not os.path.exists('filt.txt'):
        with open('filt.txt', 'w') as f:
            f.write('0')
    
    # Open the file with proper locking to prevent race conditions
    with open('filt.txt', 'r+') as file1:
        portalocker.lock(file1, portalocker.LOCK_EX)  # Lock the file
        
        current_num = int(file1.read().strip())
        print(f"Current number: {current_num}")
        
        # Move cursor to beginning and truncate file
        file1.seek(0)
        file1.truncate()
        
        # Write the incremented number
        updated_num = current_num + 1
        file1.write(str(updated_num))
        
        portalocker.unlock(file1)  # Release the lock
        
    return current_num  # Return the original number before increment