# Pacman Implementation

Documentation for the Pacman package manager implementation.

---

## Overview

**Class:** `PacmanPackageManager`
**Executable:** `pacman`
**Repositories:** core, extra, community, multilib (official only)
**AUR Support:** ❌ No
**Sudo Required:** ✅ Yes
**File:** `implementations/pacman.py` (325 lines)

---

## Description

Pacman is the official package manager for Arch Linux. It manages packages from the official Arch repositories but does not support AUR (Arch User Repository) packages.

### When to Use

- **Official packages only** - No AUR packages needed
- **Maximum stability** - Official, well-tested packages
- **Minimal dependencies** - No additional tools required
- **System administration** - Core system package management

### When Not to Use

- **Need AUR packages** - Use yay or paru instead
- **User-friendly experience** - AUR helpers provide better UX
- **Avoid sudo prompts** - AUR helpers handle sudo internally

---

## Command Patterns

### Install

```bash
sudo pacman -S --noconfirm <packages...>
```

**With system update:**
```bash
sudo pacman -Syu --noconfirm <packages...>
```

**Python equivalent:**
```python
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
result = pm.install(["vim", "git"])
```

---

### Remove

```bash
sudo pacman -R --noconfirm <packages...>
```

**With dependencies:**
```bash
sudo pacman -Rs --noconfirm <packages...>
```

**Python equivalent:**
```python
result = pm.remove(["package"], remove_dependencies=True)
```

---

### Search

```bash
pacman -Ss <query>
```

**Python equivalent:**
```python
result = pm.search("python")
```

---

### Update System

**Dry run (check for updates):**
```bash
pacman -Qu
```

**Sync databases:**
```bash
sudo pacman -Sy --noconfirm --noprogressbar --quiet
```

**Python equivalent:**
```python
# Check for updates
result = pm.update_system(dry_run=True)

# Sync databases
result = pm.update_system(dry_run=False)
```

---

### Check if Installed

```bash
pacman -Q <package>
```

**Python equivalent:**
```python
if pm.is_installed("vim"):
    print("Vim is installed")
```

---

### Get Package Info

```bash
pacman -Si <package>  # Repository info
pacman -Qi <package>  # Installed info
```

**Python equivalent:**
```python
info = pm.get_package_info("vim")
```

---

## Output Parsing

### Search Output Format

```
core/vim 9.0.1234-1
    Vi Improved, a highly configurable, improved version of the vi text editor
extra/neovim 0.9.0-1 [installed]
    Fork of Vim aiming to improve user experience, plugins, and GUIs
```

**Parsing Logic:**

```python
# Regex pattern
pattern = r"^([\w-]+)/([\w\-\.]+)\s+([\w\.\-:]+)(?:\s+\[installed\])?"

# Matches:
# Group 1: repository (core, extra, etc.)
# Group 2: package name
# Group 3: version
# [installed] flag indicates if installed
```

---

### Package Info Output Format

```
Repository      : core
Name            : vim
Version         : 9.0.1234-1
Description     : Vi Improved...
Architecture    : x86_64
URL             : https://www.vim.org
Licenses        : custom:vim
Groups          : None
Provides        : xxd  vim-minimal
Depends On      : glibc  libgcrypt  ...
Optional Deps   : python: Python support
Conflicts With  : gvim
Replaces        : None
Download Size   : 1.50 MiB
Installed Size  : 3.50 MiB
```

**Parsing Logic:**

Parses key-value pairs from output:
- `Name` → package name
- `Version` → version string
- `Description` → description
- `Repository` → repository name
- `Installed Size` → size
- `Depends On` → dependencies list

---

## Sudo Handling

Pacman requires sudo for install, remove, and update operations.

### Command Construction

```python
# Install command
command = ["sudo", str(self.executable_path), "-S", "--noconfirm"] + packages

# Remove command
command = ["sudo", str(self.executable_path), "-R", "--noconfirm"] + packages

# Update command
command = ["sudo", str(self.executable_path), "-Sy", "--noconfirm", ...]
```

### Implications

- **User must have sudo privileges**
- **May prompt for password** (depending on sudo configuration)
- **Multiple prompts possible** (if sudo timeout expires)
- **Non-interactive environments may fail** (if password required)

### Best Practices

1. **Pre-authenticate with sudo:**
   ```bash
   sudo -v  # Enter password once
   # Then run Python script
   ```

2. **Configure sudo timeout:**
   ```bash
   sudo visudo
   # Add: Defaults timestamp_timeout=30
   ```

3. **Use AUR helpers for better UX:**
   ```python
   # Prefer paru/yay over pacman
   pm = PackageManagerFactory.create_auto(prefer_aur_helper=True)
   ```

---

## Limitations

1. **No AUR Support**
   - Cannot install packages from AUR
   - Limited to official repositories
   - Use yay or paru for AUR packages

2. **Requires Sudo**
   - User must have sudo privileges
   - May prompt for password multiple times
   - Difficult in non-interactive environments

3. **No Automatic Dependency Removal**
   - `remove()` with `remove_dependencies=False` leaves orphaned dependencies
   - Manual cleanup required: `pacman -Qdtq | pacman -Rs -`

4. **Limited Progress Information**
   - No progress callbacks
   - No percentage complete
   - All-or-nothing operation

---

## Examples

### Basic Usage

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerType

# Create pacman instance
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)

# Install packages
result = pm.install(["vim", "git", "tmux"])
if result.success:
    print("✓ Installed successfully")

# Search for packages
result = pm.search("python")
for pkg in result.packages:
    print(f"{pkg.repository}/{pkg.name} {pkg.version}")

# Check if installed
if pm.is_installed("vim"):
    print("Vim is installed")

# Get package info
info = pm.get_package_info("vim")
print(f"{info.name} {info.version}")
```

---

### Force Pacman (Avoid AUR Helpers)

```python
# Explicitly use pacman, not AUR helpers
pm = PackageManagerFactory.create_auto(prefer_aur_helper=False)

# Or force pacman
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
```

---

### Handle Sudo Prompts

```python
import subprocess

# Pre-authenticate
subprocess.run(["sudo", "-v"], check=True)

# Now use package manager (won't prompt for password)
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
result = pm.install(["package"])
```

---

## Comparison with AUR Helpers

| Feature | Pacman | Yay | Paru |
|---------|--------|-----|------|
| **AUR Support** | ❌ No | ✅ Yes | ✅ Yes |
| **Sudo Required** | ✅ Yes | ❌ No | ❌ No |
| **Repositories** | Official only | Official + AUR | Official + AUR |
| **Performance** | Fast | Medium | Fast |
| **Stability** | Highest | High | High |
| **User Experience** | Basic | Better | Best |

---

## Technical Details

### Class Structure

```python
class PacmanPackageManager(PackageManager):
    """Pacman package manager implementation."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.PACMAN

    def _find_executable(self) -> Path | None:
        """Find pacman executable."""
        executable = shutil.which("pacman")
        return Path(executable) if executable else None

    # Implement all abstract methods...
```

### Executable Detection

```python
# Uses shutil.which() to find "pacman" in PATH
executable = shutil.which("pacman")
# Returns: /usr/bin/pacman (or None if not found)
```

### Error Handling

- **Executable not found:** Raises `PackageManagerError`
- **Package not found:** Returns `InstallResult(success=False, packages_failed=[...])`
- **Permission denied:** Returns `InstallResult(success=False, error_message="...")`
- **Command timeout:** Raises `PackageManagerError`

---

## See Also

- [Yay Implementation](yay.md) - AUR helper alternative
- [Paru Implementation](paru.md) - Preferred AUR helper
- [API Reference](../api_reference.md) - Complete API documentation
- [Usage Guide](../usage_guide.md) - Usage patterns and examples

---

**Official Documentation:** https://wiki.archlinux.org/title/Pacman
