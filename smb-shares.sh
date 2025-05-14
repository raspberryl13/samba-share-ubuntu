# smb-shares.sh: Automate Samba share setup with smb-shares.py
# Run on Debian/Ubuntu to create Windows-compatible shared folders
# Compatible with standard systems and LXC containers

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)."
  exit 1
fi

# Install Samba
echo "Installing Samba..."
apt update
apt install -y samba || { echo "Samba installation failed."; exit 1; }

# Check if smb-shares.py exists
if [ ! -f "smb-shares.py" ]; then
  echo "Error: smb-shares.py not found in current directory."
  exit 1
fi

# Make smb-shares.py executable
chmod +x smb-shares.py

# Prompt for folder and validate
while true; do
  read -p "Enter folder to share (e.g., /home/user/myshare): " folder
  if [ -d "$folder" ]; then
    break
  else
    echo "Folder does not exist."
    read -p "Create folder? (y/n): " create_folder
    if [ "$create_folder" = "y" ]; then
      mkdir -p "$folder"
      chmod 777 "$folder"
      echo "Folder $folder created with permissions 777."
      break
    else
      echo "Please create the folder first (e.g., sudo mkdir -p /home/user/myshare; sudo chmod 777 /home/user/myshare)."
    fi
  fi
done

# Warn about existing users
echo "Warning: If creating a new Samba user, choose a username that does not already exist."
echo "Check existing users with: cat /etc/passwd"

# Run Python script
echo "Running smb-shares.py..."
python3 smb-shares.py || { echo "smb-shares.py failed."; exit 1; }

# Restart and enable Samba
echo "Restarting Samba..."
systemctl restart smbd || { echo "Failed to restart smbd."; exit 1; }
systemctl enable smbd

# Output success
echo "Samba installation and configuration completed."
echo "Access share from Windows: \\\\<host-ip>\\<share-name> (e.g., \\192.168.1.x\\myshare)"
echo "Login with username/password set in smb-shares.py."

# Troubleshooting
echo "Troubleshooting:"
echo "1. If user creation fails:"
echo "   sudo useradd -m <username>"
echo "   sudo passwd <username>"
echo "   sudo smbpasswd -a <username>"
echo "2. Edit Samba config if needed:"
echo "   sudo nano /etc/samba/smb.conf"
echo "3. Restart Samba service:"
echo "   sudo systemctl restart smbd"
echo "   sudo systemctl enable smbd"
echo "4. Check Samba status:"
echo "   systemctl status smbd"
echo "5. Test share from Linux:"
echo "   smbclient //<host-ip>/<share-name> -U <username>"

# Firewall note
echo "Note: Ensure your firewall allows SMB ports (137-139, 445). For example, on UFW:"
echo "sudo ufw allow Samba"
echo "Or consult your router/firewall documentation."
