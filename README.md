# Samba Share Setup
Automates Windows-compatible shared folders (SMB) on Debian/Ubuntu, including containers.

## Usage
1. Clone repo: `git clone <repo-url>`
2. Create folder: `sudo mkdir -p /home/user/myshare; sudo chmod 777 /home/user/myshare`
3. Run: `sudo ./smb-shares.sh`
4. Follow prompts for folder and user setup.

## Requirements
- Debian/Ubuntu system
- Samba (`apt install samba`)
- Python 3 (`apt install python3`)

## Notes
- Ensure firewall allows ports 137–139, 445.
- Backup configs before modifying `/etc/samba/smb.conf`.

## License
MIT License
