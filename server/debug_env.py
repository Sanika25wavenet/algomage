from dotenv import dotenv_values
import os

def debug_env():
    config = dotenv_values(".env")
    print("Keys found in .env:")
    for key in config.keys():
        print(f" - {key}")

    # Check for suspicious keys
    if "attendance-cluster" in str(config):
         print("\nWARNING: 'attendance-cluster' detected in parsed values/keys!")

if __name__ == "__main__":
    debug_env()
