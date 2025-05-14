import os
import subprocess
import getpass
import re

def validate_path(path):
    """Validate if the folder exists and is a directory."""
    return os.path.isdir(path) and os.path.exists(path)

def validate_username(username):
    """Validate username (alphanumeric, 3-32 chars)."""
    return bool(re.match(r'^[a-zA-Z0-9]{3,32}$', username))

def create_samba_user(username, password):
    """Create system user and add to Samba."""
    try:
        subprocess.run(['useradd', '-m', username], check=True)
        subprocess.run(['passwd', username], input=f"{password}\n{password}\n", text=True, check=True)
        subprocess.run(['smbpasswd', '-a', username], input=f"{password}\n{password}\n", text=True, check=True)
        print(f"User {username} created and added to Samba.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating user: {e}")
        return False
    return True

def update_smb_conf(share_name, path, username):
    """Update smb.conf with new share."""
    share_config = f"""
[{share_name}]
path = {path}
browsable = yes
writable = yes
guest ok = no
read only = no
valid users = {username}
create mask = 0777
directory mask = 0777
"""
    try:
        with open('/etc/samba/smb.conf', 'a') as f:
            f.write(share_config)
        subprocess.run(['systemctl', 'restart', 'smbd'], check=True)
        print(f"Share '{share_name}' added to smb.conf and Samba restarted.")
    except (IOError, subprocess.CalledProcessError) as e:
        print(f"Error updating smb.conf: {e}")
        return False
    return True

def main():
    print("Samba Share Setup Script")
    
    # Prompt for folder to share
    while True:
        folder_path = input("Which folder would you like to share? (e.g., /srv/samba/myshare): ").strip()
        if validate_path(folder_path):
            break
        print("Invalid or non-existent folder. Please create the folder first and try again.")

    # Derive share name from folder path (e.g., /srv/samba/myshare -> myshare)
    share_name = os.path.basename(folder_path)

    # Prompt for Windows account creation
    create_account = input("Would you like to create a Windows account? (y/n): ").strip().lower()
    
    if create_account == 'y':
        # Prompt for username
        while True:
            username = input("Enter username (alphanumeric, 3-32 characters): ").strip()
            if validate_username(username):
                break
            print("Invalid username. Use alphanumeric characters, 3-32 length.")
        
        # Prompt for password
        while True:
            password = getpass.getpass("Enter password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            if password == confirm_password and len(password) >= 6:
                break
            print("Passwords do not match or are too short (min 6 chars). Try again.")

        # Create user and update Samba
        if not create_samba_user(username, password):
            print("Failed to create user. Exiting.")
            return
        
        # Update smb.conf
        if not update_smb_conf(share_name, folder_path, username):
            print("Failed to configure share. Exiting.")
            return
    else:
        # Use existing sambauser (assumes already set up)
        username = 'sambauser'
        if not update_smb_conf(share_name, folder_path, username):
            print("Failed to configure share. Exiting.")
            return

    print(f"Share '{share_name}' configured successfully!")
    print(f"Access from Windows: \\\\<main-pc-ip>\\{share_name} (e.g., \\\\192.168.50.x\\{share_name})")
    print(f"Login: {username}, password: <your-password>")

if __name__ == '__main__':
    main()