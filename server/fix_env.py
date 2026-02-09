import os

def fix_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        print(".env not found")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    buffer = ""
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if buffer:
                new_lines.append(buffer + "\n")
                buffer = ""
            new_lines.append(line)
            continue
        
        if stripped.startswith("MONGODB_URL="):
            buffer = stripped
        elif buffer and not "=" in stripped:
            # Likely a continuation of the previous line
            buffer += stripped
        else:
            if buffer:
                new_lines.append(buffer + "\n")
                buffer = ""
            new_lines.append(line)
    
    if buffer:
        new_lines.append(buffer + "\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print("Fixed .env file formatting.")

if __name__ == "__main__":
    fix_env()
