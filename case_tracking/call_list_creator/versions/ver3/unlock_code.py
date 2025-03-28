import hashlib
import datetime as dt

# Secret key (fixed for security)
SECRET_KEY = "O Romeo, Romeo! wherefore art thou Romeo?"

def generate_unlock_code(machine_guid):
    """Generate an unlock code that changes every 5 minutes and is unique per computer."""
    current_time = dt.datetime.now()
    rounded_minutes = (current_time.minute // 5) * 5  # Round to nearest 5-minute mark
    time_string = f"{current_time.year}-{current_time.month}-{current_time.day} {current_time.hour}:{rounded_minutes:02d}"

    unlock_string = time_string + SECRET_KEY + machine_guid
    return hashlib.sha256(unlock_string.encode()).hexdigest()[:8]  # Shortened hash

if __name__ == "__main__":
    # Ask the user to enter the Machine GUID
    machine_guid = input("Enter the Machine GUID: ").strip()
    
    if not machine_guid:
        print("Error: Machine GUID cannot be empty!")
    else:
        unlock_code = generate_unlock_code(machine_guid)
        print("\nYour unlock code is:", unlock_code)
