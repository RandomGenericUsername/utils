# Yay Implementation

Documentation for the Yay AUR helper implementation.

---

## Overview

**Class:** `YayPackageManager`
**Executable:** `yay`
**Repositories:** Official + AUR
**AUR Support:** ✅ Yes
**Sudo Required:** ❌ No (handles internally)
**Language:** Go
**File:** `implementations/yay.py` (332 lines)

---

## Description

Yay (Yet Another Yogurt) is an AUR helper written in Go. It provides access to both official Arch repositories and the AUR (Arch User Repository), with a user-friendly interface that handles sudo internally.

### When to Use

- **Need AUR packages** - Access to thousands of AUR packages
- **Better user experience** - Handles sudo internally, fewer prompts
- **Yay already installed** - Use what's available
- **Compatibility** - Well-established, widely used

### When Not to Use

- **Prefer performance** - Paru is faster (written in Rust)
- **Official packages only** - Use pacman instead
- **Maximum stability** - Stick to official repos with pacman

---

## Installation

Yay must be installed from AUR:

```bash
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

Or using another AUR helper:
```bash
paru -S yay
```

---

## Command Patterns

### Install

```bash
yay -S --noconfirm <packages...>
```

**With system update:**
```bash
yay -Syu --noconfirm <packages...>
```

**Python equivalent:**
```python
pm = PackageManagerFactory.create(PackageManagerType.YAY)
result = pm.install(["vim", "google-chrome"])  # google-chrome is AUR
```

---

### Remove

```bash
yay -R --noconfirm <packages...>
```

**With dependencies:**
```bash
yay -Rs --noconfirm <packages...>
```

**Python equivalent:**
```python
result = pm.remove(["package"], remove_dependencies=True)
```

---

### Search

```bash
yay -Ss <query>
```

**Python equivalent:**
```python
result = pm.search("chrome")  # Searches both official and AUR
```

---

### Update System

**Dry run (check for updates):**
```bash
yay -Qu
```

**Sync databases:**
```bash
yay -Sy --noconfirm --noprogressbar --quiet
```

**Python equivalent:**
```python
# Check for updates
result = pm.update_system(dry_run=True)

# Sync databases
result = pm.update_system(dry_run=False)
```

---

## Output Parsing

### Search Output Format

```
core/vim 9.0.1234-1
    Vi Improved, a highly configurable, improved version of the vi text editor
aur/google-chrome 114.0.5735.90-1 (+1234 0.56) [installed]
    The popular and trusted web browser by Google (Stable Channel)
```

**Parsing Logic:**

```python
# Regex pattern (same as pacman, but also matches 'aur/')
pattern = r"^([\w-]+)/([\w\-\.]+)\s+([\w\.\-:]+)(?:\s+\[installed\])?"

# Matches:
# Group 1: repository (core, extra, aur, etc.)
# Group 2: package name
# Group 3: version
# [installed] flag indicates if installed
```

**Key Difference from Pacman:**
- Recognizes `aur/` repository prefix
- Shows AUR package statistics (votes, popularity)

---

## Sudo Handling

Yay handles sudo internally - no need to prefix commands with `sudo`.

### Command Construction

```python
# Install command (NO sudo prefix)
command = [str(self.executable_path), "-S", "--noconfirm"] + packages

# Remove command (NO sudo prefix)
command = [str(self.executable_path), "-R", "--noconfirm"] + packages

# Update command (NO sudo prefix)
command = [str(self.executable_path), "-Sy", "--noconfirm", ...]
```

### Advantages

- **Fewer password prompts** - Yay prompts only when needed
- **Better UX** - More user-friendly than pacman
- **Non-interactive friendly** - Works better in scripts

### How It Works

Yay internally calls `sudo` when needed for privileged operations, but manages the prompts itself.

---

## AUR Support

### What is AUR?

The Arch User Repository (AUR) is a community-driven repository for Arch users. It contains package descriptions (PKGBUILDs) that allow you to compile packages from source.

### AUR Package Installation

When installing AUR packages, yay:
1. Downloads PKGBUILD from AUR
2. Reviews dependencies
3. Builds package from source
4. Installs built package

### Example AUR Packages

```python
pm = PackageManagerFactory.create(PackageManagerType.YAY)

# Install AUR packages
aur_packages = [
    "google-chrome",
    "visual-studio-code-bin",
    "spotify",
    "slack-desktop",
]

result = pm.install(aur_packages)
```

---

## Performance

### Speed Comparison

| Operation | Pacman | Yay | Paru |
|-----------|--------|-----|------|
| **Search** | Fast | Medium | Fast |
| **Install (official)** | Fast | Medium | Fast |
| **Install (AUR)** | N/A | Medium | Fast |
| **Memory Usage** | Low | Medium | Low |

### Why Slower than Paru?

- **Language:** Go vs Rust (Paru)
- **Implementation:** Different optimization strategies
- **Not significant:** Difference is usually negligible for typical use

---

## Limitations

1. **Slower than Paru**
   - Written in Go, not as optimized as Paru (Rust)
   - Noticeable only for large operations

2. **AUR Build Time**
   - AUR packages must be built from source
   - Can take significant time for large packages
   - No progress indication during build

3. **No Progress Callbacks**
   - Same as pacman
   - No way to monitor installation progress

4. **Requires Build Tools**
   - Needs `base-devel` for building AUR packages
   - Additional disk space for build process

---

## Examples

### Basic Usage

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerType

# Create yay instance
pm = PackageManagerFactory.create(PackageManagerType.YAY)

# Install official packages
result = pm.install(["vim", "git", "tmux"])

# Install AUR packages
result = pm.install(["google-chrome", "spotify"])

# Install mixed (official + AUR)
result = pm.install(["vim", "google-chrome"])

# Search (searches both official and AUR)
result = pm.search("chrome")
for pkg in result.packages:
    repo_type = "AUR" if pkg.repository == "aur" else "Official"
    print(f"[{repo_type}] {pkg.name} {pkg.version}")
```

---

### Check if Package is from AUR

```python
info = pm.get_package_info("google-chrome")
if info and info.repository == "aur":
    print("This is an AUR package")
```

---

### Install with Dependency Check

```python
# Ensure base-devel is installed (required for AUR)
if not pm.is_installed("base-devel"):
    print("Installing base-devel (required for AUR packages)...")
    pm.install(["base-devel"])

# Now install AUR packages
result = pm.install(["aur-package"])
```

---

## Comparison with Other Managers

| Feature | Pacman | Yay | Paru |
|---------|--------|-----|------|
| **AUR Support** | ❌ No | ✅ Yes | ✅ Yes |
| **Sudo Required** | ✅ Yes | ❌ No | ❌ No |
| **Language** | C | Go | Rust |
| **Performance** | Fast | Medium | Fast |
| **User Experience** | Basic | Good | Excellent |
| **Preference** | 3rd | 2nd | 1st |

---

## Technical Details

### Class Structure

```python
class YayPackageManager(PackageManager):
    """Yay AUR helper implementation."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.YAY

    def _find_executable(self) -> Path | None:
        """Find yay executable."""
        executable = shutil.which("yay")
        return Path(executable) if executable else None

    # Implement all abstract methods...
```

### Executable Detection

```python
# Uses shutil.which() to find "yay" in PATH
executable = shutil.which("yay")
# Returns: /usr/bin/yay (or None if not found)
```

### Error Handling

- **Executable not found:** Raises `PackageManagerError`
- **Package not found:** Returns `InstallResult(success=False, packages_failed=[...])`
- **Build failure:** Returns `InstallResult(success=False, error_message="...")`
- **Dependency conflict:** Returns `InstallResult(success=False, error_message="...")`

---

## Migration from Pacman

If you're currently using pacman and want to switch to yay:

```python
# Before (pacman only)
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
result = pm.install(["vim"])  # Official packages only

# After (yay - official + AUR)
pm = PackageManagerFactory.create(PackageManagerType.YAY)
result = pm.install(["vim"])  # Official packages
result = pm.install(["google-chrome"])  # AUR packages
```

Or use auto-detection:
```python
# Automatically prefers yay over pacman
pm = PackageManagerFactory.create_auto()
```

---

## Troubleshooting

### Issue: Yay not found

**Solution:**
```bash
# Install yay from AUR
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si
```

### Issue: Build failures

**Solution:**
```bash
# Ensure base-devel is installed
sudo pacman -S base-devel

# Clear yay cache
yay -Sc
```

### Issue: Slow AUR builds

**Solution:**
- Use paru instead (faster)
- Pre-build packages manually
- Use binary AUR packages (e.g., `package-bin` instead of `package`)

---

## See Also

- [Pacman Implementation](pacman.md) - Official package manager
- [Paru Implementation](paru.md) - Preferred AUR helper (faster)
- [API Reference](../api_reference.md) - Complete API documentation
- [Usage Guide](../usage_guide.md) - Usage patterns and examples

---

**Official Repository:** https://github.com/Jguer/yay
**AUR Page:** https://aur.archlinux.org/packages/yay
