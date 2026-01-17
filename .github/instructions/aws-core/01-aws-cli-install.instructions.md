# AWS CLI Installation Instructions

This instruction file helps GitHub Copilot assist developers with installing and verifying AWS CLI v2. When a developer uses `/aws-cli` commands, Copilot should execute operations silently and display only formatted results.

**Important:** Never show raw output. Always parse and format results automatically.

<Commands>

| Command | Description |
|---------|-------------|
| `/aws-cli install` | Install AWS CLI v2 based on OS |
| `/aws-cli verify` | Verify AWS CLI installation |
| `/aws-cli version` | Show AWS CLI version |
| `/aws-cli upgrade` | Upgrade AWS CLI to latest version |
| `/aws-cli uninstall` | Uninstall AWS CLI |

</Commands>

<Goals>
- Install AWS CLI v2 on macOS, Linux, or Windows
- Verify successful installation
- Ensure correct version is installed
- Provide upgrade path for existing installations
</Goals>

<Limitations>
- Requires administrator/sudo access for installation
- Windows requires PowerShell with admin privileges
- Some Linux distributions may need additional dependencies
</Limitations>

<BuildInstructions>

## /aws-cli install

**Execution flow:**
1. Detect operating system
2. Download appropriate installer
3. Run installation
4. Verify installation
5. Display success message

**For macOS:**
```bash
# Download the installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

# Install (requires sudo)
sudo installer -pkg AWSCLIV2.pkg -target /

# Cleanup
rm AWSCLIV2.pkg
```

**For Linux (x86_64):**
```bash
# Download the installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip
unzip awscliv2.zip

# Install (requires sudo)
sudo ./aws/install

# Cleanup
rm -rf awscliv2.zip aws/
```

**For Linux (ARM):**
```bash
# Download the installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"

# Unzip
unzip awscliv2.zip

# Install (requires sudo)
sudo ./aws/install

# Cleanup
rm -rf awscliv2.zip aws/
```

**For Windows (PowerShell as Admin):**
```powershell
# Download the installer
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "AWSCLIV2.msi"

# Install
Start-Process msiexec.exe -Wait -ArgumentList '/I AWSCLIV2.msi /quiet'

# Cleanup
Remove-Item "AWSCLIV2.msi"
```

**Display this output:**
```
╔══════════════════════════════════════════════════════════════╗
║           🔧 INSTALLING AWS CLI v2                           ║
╠══════════════════════════════════════════════════════════════╣
║  Operating System:  macOS (detected)                         ║
╠══════════════════════════════════════════════════════════════╣
║  Progress:                                                   ║
║  ├── ✅ Downloaded AWSCLIV2.pkg                              ║
║  ├── ✅ Installed AWS CLI                                    ║
║  └── ✅ Cleaned up installer                                 ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ AWS CLI v2 installed successfully!                       ║
║                                                              ║
║  Version: aws-cli/2.15.0 Python/3.11.6 Darwin/23.0.0         ║
║  Path:    /usr/local/bin/aws                                 ║
╠══════════════════════════════════════════════════════════════╣
║  💡 Next: Run `/aws-profile setup` to configure credentials  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## /aws-cli verify

**Execution flow:**
1. Check if AWS CLI is installed
2. Verify version
3. Check PATH configuration
4. Display status

**Internal command:**
```bash
aws --version
which aws
```

**Display this output:**
```
╔══════════════════════════════════════════════════════════════╗
║           ✅ AWS CLI VERIFICATION                            ║
╠══════════════════════════════════════════════════════════════╣
║  Status:    Installed                                        ║
║  Version:   aws-cli/2.15.0 Python/3.11.6 Darwin/23.0.0       ║
║  Path:      /usr/local/bin/aws                               ║
║  Config:    ~/.aws/config (exists)                           ║
║  Creds:     ~/.aws/credentials (exists)                      ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ AWS CLI is ready to use!                                 ║
╚══════════════════════════════════════════════════════════════╝
```

**If not installed:**
```
╔══════════════════════════════════════════════════════════════╗
║           ❌ AWS CLI NOT FOUND                               ║
╠══════════════════════════════════════════════════════════════╣
║  Status:    Not installed                                    ║
║                                                              ║
║  💡 Run `/aws-cli install` to install AWS CLI v2             ║
╚══════════════════════════════════════════════════════════════╝
```

---

## /aws-cli version

**Internal command:**
```bash
aws --version
```

**Display this output:**
```
╔══════════════════════════════════════════════════════════════╗
║           📋 AWS CLI VERSION                                 ║
╠══════════════════════════════════════════════════════════════╣
║  AWS CLI:   2.15.0                                           ║
║  Python:    3.11.6                                           ║
║  OS:        Darwin/23.0.0 (macOS)                            ║
║  Path:      /usr/local/bin/aws                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## /aws-cli upgrade

**Execution flow:**
1. Check current version
2. Download latest installer
3. Run upgrade installation
4. Verify new version
5. Display success message

**For macOS:**
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
rm AWSCLIV2.pkg
```

**For Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2.zip aws/
```

**Display this output:**
```
╔══════════════════════════════════════════════════════════════╗
║           ⬆️  UPGRADING AWS CLI                              ║
╠══════════════════════════════════════════════════════════════╣
║  Current Version:   2.13.0                                   ║
║  Latest Version:    2.15.0                                   ║
╠══════════════════════════════════════════════════════════════╣
║  Progress:                                                   ║
║  ├── ✅ Downloaded latest installer                          ║
║  ├── ✅ Installed update                                     ║
║  └── ✅ Cleaned up                                           ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ AWS CLI upgraded to 2.15.0                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

## /aws-cli uninstall

**For macOS:**
```bash
sudo rm -rf /usr/local/aws-cli
sudo rm /usr/local/bin/aws
sudo rm /usr/local/bin/aws_completer
```

**For Linux:**
```bash
sudo rm -rf /usr/local/aws-cli
sudo rm /usr/local/bin/aws
sudo rm /usr/local/bin/aws_completer
```

**For Windows (PowerShell as Admin):**
```powershell
Start-Process msiexec.exe -Wait -ArgumentList '/X AWSCLIV2.msi /quiet'
```

**Display this output:**
```
╔══════════════════════════════════════════════════════════════╗
║           🗑️  UNINSTALLING AWS CLI                           ║
╠══════════════════════════════════════════════════════════════╣
║  Progress:                                                   ║
║  ├── ✅ Removed AWS CLI binaries                             ║
║  ├── ✅ Removed aws command                                  ║
║  └── ✅ Removed aws_completer                                ║
╠══════════════════════════════════════════════════════════════╣
║  ✅ AWS CLI uninstalled successfully!                        ║
║                                                              ║
║  ⚠️  Note: ~/.aws/ config files were preserved.              ║
║     Delete manually if no longer needed.                     ║
╚══════════════════════════════════════════════════════════════╝
```

</BuildInstructions>

<DockerCommands>

These commands map to Docker image execution:

| Copilot Command | Docker Command |
|-----------------|----------------|
| `/aws-cli verify` | `docker run aws-agents-video-transcript-buddy:1.0.0 check_aws_cli` |

**Note:** AWS CLI is pre-installed in the Docker image, so `install`, `upgrade`, and `uninstall` commands are not applicable inside Docker.

</DockerCommands>

<CommonErrors>

| Error | Cause | Fix |
|-------|-------|-----|
| `command not found: aws` | AWS CLI not installed | Run `/aws-cli install` |
| `permission denied` | No sudo access | Run with administrator privileges |
| `unable to locate package` | Missing dependencies (Linux) | Install `unzip` and `curl` first |
| Old version shown after upgrade | PATH issue | Restart terminal or run `hash -r` |

</CommonErrors>

<AlwaysNever>

Always:
- Verify installation after install/upgrade
- Clean up downloaded installer files
- Check for existing installation before installing
- Display version after successful operations

Never:
- Install AWS CLI v1 (always use v2)
- Leave installer files after installation
- Skip verification step
- Run without appropriate permissions

</AlwaysNever>