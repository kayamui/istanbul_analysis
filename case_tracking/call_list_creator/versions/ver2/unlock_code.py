import hashlib
from datetime import datetime

# Secret key and current date
secret_key = "O Romeo, Romeo! wherefore art thou Romeo?"
current_time = datetime.now().strftime('%Y-%m-%d')

# Generate the unlock code
unlock_string = current_time + secret_key
unlock_code = hashlib.sha256(unlock_string.encode()).hexdigest()[:8]

print("Your unlock code is:", unlock_code)
