# utility.py
from datetime import datetime

def validate_dob(dob_str :str) -> bool:  #parameter dob_str is expected to be of type str 

    
  
    try:
        datetime.strptime(dob_str, "%Y-%m-%d")
        return True
    except ValueError:
        
        return False


def validate_username(username: str) -> bool:
    
    return len(username.strip()) >= 3
