# Paru Implementation

Documentation for the Paru AUR helper implementation.

---

## Overview

**Class:** `ParuPackageManager`
**Executable:** `paru`
**Repositories:** Official + AUR
**AUR Support:** ✅ Yes
**Sudo Required:** ❌ No (handles internally)
**Language:** Rust
**File:** `implementations/paru.py` (331 lines)
**Preference:** 🥇 1st choice (recommended)

---

## Description

Paru is a modern AUR helper written in Rust, designed as a feature-rich alternative to yay. It provides access to both official Arch repositories and the AUR with excellent performance and user experience.

### Why Paru is Preferred

1. **Performance** - Written in Rust, faster than yay (Go)
2. **Modern** - Active development, modern codebase
3. **Feature-rich** - More features than yay
4. **Memory efficient** - Lower memory footprint
5. **Better AUR integration** - Enhanced AUR package review features

### When to Use

- **Default choice** - Best overall AUR helper
- **Need AUR packages** - Access to thousands of AUR packages
- **Performance matters** - Faster than yay
- **Modern features** - Latest AUR helper features

### When Not to Use

- **Not installed** - Fall back to yay or pacman
- **Official packages only** - Use pacman instead
- **Compatibility concerns** - Yay is more established

---

## Installation

Paru must be installed from AUR:

```bash
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
```

Or using yay:
```bash
yay -S paru
```

---

## Command Patterns

### Install

```bash
paru -S --noconfirm <packages...>
```

**With system update:**
```bash
paru -Syu --noconfirm <packages...>
```

**Python equivalent:**
```python
pm = PackageManagerFactory.create(PackageManagerType.PARU)
result = pm.install(["vim", "google-chrome"])  # google-chrome is AUR
```

---

### Remove

```bash
paru -R --noconfirm <packages...>
```

**With dependencies:**
```bash
paru -Rs --noconfirm <packages...>
```

**Python equivalent:**
```python
result = pm.remove(["package"], remove_dependencies=True)
```

---

### Search

```bash
paru -Ss <query>
```

**Python equivalent:**
```python
result = pm.search("chrome")  # Searches both official and AUR
```

---

### Update System

**Dry run (check for updates):**
```bash
paru -Qu
```

**Sync databases:**
```bash
paru -Sy --noconfirm --noprogressbar --quiet
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

Identical to yay:

```
core/vim 9.0.1234-1
    Vi Improved, a highly configurable, improved version of the vi text editor
aur/google-chrome 114.0.5735.90-1 (+1234 0.56) [installed]
    The popular and trusted web browser by Google (Stable Channel)
```

**Parsing Logic:**

```python
# Regex pattern (same as yay)
pattern = r"^([\w-]+)/([\w\-\.]+)\s+([\w\.\-:]+)(?:\s+\[installed\])?"

# Matches:
# Group 1: repository (core, extra, aur, etc.)
# Group 2: package name
# Group 3: version
# [installed] flag indicates if installed
```

---

## Sudo Handling

Paru handles sudo internally - identical to yay.

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

- **Fewer password prompts** - Paru prompts only when needed
- **Better UX** - More user-friendly than pacman
- **Non-interactive friendly** - Works well in scripts
- **Smart caching** - Remembers sudo credentials better than yay

---

## AUR Support

### Enhanced AUR Features

Paru provides enhanced AUR features compared to yay:

1. **Better PKGBUILD review** - Interactive review before building
2. **Faster dependency resolution** - Rust-based optimization
3. **Better error messages** - More informative build failures
4. **Improved caching** - Faster repeated operations

### Example AUR Packages

```python
pm = PackageManagerFactory.create(PackageManagerType.PARU)

# Install AUR packages
aur_packages = [
    "google-chrome",
    "visual-studio-code-bin",
    "spotify",
    "slack-desktop",
    "brave-bin",
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
| **Dependency Resolution** | Fast | Medium | Fast |

### Why Faster than Yay?

1. **Rust** - Compiled to native code, highly optimized
2. **Better algorithms** - Improved dependency resolution
3. **Efficient caching** - Smart caching strategies
4. **Parallel operations** - Better parallelization

### Benchmarks

Typical performance improvements over yay:
- **Search:** 10-20% faster
- **Dependency resolution:** 20-30% faster
- **Memory usage:** 15-25% lower

---

## Paru-Specific Features

### Features Not in Yay

1. **Better PKGBUILD review**
   - Interactive review before building
   - Syntax highlighting
   - Diff viewing

2. **News reader**
   - Shows Arch Linux news
   - Warns about manual interventions

3. **Batch operations**
   - Better handling of multiple packages
   - Smarter dependency ordering

4. **Configuration**
   - More configuration options
   - Better defaults

---

## Limitations

Same as yay:

1. **AUR Build Time**
   - AUR packages must be built from source
   - Can take significant time for large packages
   - No progress indication during build

2. **No Progress Callbacks**
   - No way to monitor installation progress
   - All-or-nothing operation

3. **Requires Build Tools**
   - Needs `base-devel` for building AUR packages
   - Additional disk space for build process

---

## Examples

### Basic Usage

```python
from dotfiles_package_manager import PackageManagerFactory, PackageManagerType

# Create paru instance
pm = PackageManagerFactory.create(PackageManagerType.PARU)

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

### Auto-Detection (Prefers Paru)

```python
# Factory automatically prefers paru
pm = PackageManagerFactory.create_auto()

# Check which manager was selected
print(f"Using: {pm.manager_type.value}")
# Output: Using: paru (if paru is installed)
```

---

### Force Paru

```python
# Explicitly require paru
from dotfiles_package_manager import PackageManagerError

try:
    pm = PackageManagerFactory.create(PackageManagerType.PARU)
except PackageManagerError:
    print("Paru not installed!")
    print("Install with: git clone https://aur.archlinux.org/paru.git && cd paru && makepkg -si")
```

---

## Comparison with Other Managers

| Feature | Pacman | Yay | Paru |
|---------|--------|-----|------|
| **AUR Support** | ❌ No | ✅ Yes | ✅ Yes |
| **Sudo Required** | ✅ Yes | ❌ No | ❌ No |
| **Language** | C | Go | Rust |
| **Performance** | Fast | Medium | Fast |
| **Memory Usage** | Low | Medium | Low |
| **User Experience** | Basic | Good | Excellent |
| **AUR Features** | N/A | Good | Excellent |
| **Preference** | 3rd | 2nd | 🥇 1st |

---

## Technical Details

### Class Structure

```python
class ParuPackageManager(PackageManager):
    """Paru AUR helper implementation."""

    @property
    def manager_type(self) -> PackageManagerType:
        return PackageManagerType.PARU

    def _find_executable(self) -> Path | None:
        """Find paru executable."""
        executable = shutil.which("paru")
        return Path(executable) if executable else None

    # Implement all abstract methods...
```

### Implementation Notes

- **Nearly identical to yay** - Same command patterns
- **Only difference:** Executable name (`paru` vs `yay`)
- **Could be refactored** - Share code with yay implementation
- **Performance difference** - Due to paru binary, not Python code

---

## Migration Guide

### From Pacman to Paru

```python
# Before (pacman only)
pm = PackageManagerFactory.create(PackageManagerType.PACMAN)
result = pm.install(["vim"])  # Official packages only

# After (paru - official + AUR)
pm = PackageManagerFactory.create(PackageManagerType.PARU)
result = pm.install(["vim"])  # Official packages
result = pm.install(["google-chrome"])  # AUR packages
```

### From Yay to Paru

```python
# Before (yay)
pm = PackageManagerFactory.create(PackageManagerType.YAY)

# After (paru) - same API, better performance
pm = PackageManagerFactory.create(PackageManagerType.PARU)

# Or use auto-detection (prefers paru)
pm = PackageManagerFactory.create_auto()
```

---

## Troubleshooting

### Issue: Paru not found

**Solution:**
```bash
# Install paru from AUR
git clone https://aur.archlinux.org/paru.git
cd paru && makepkg -si
```

### Issue: Build failures

**Solution:**
```bash
# Ensure base-devel is installed
sudo pacman -S base-devel

# Clear paru cache
paru -Sc

# Update paru itself
paru -S paru
```

### Issue: Slower than expected

**Check:**
- Ensure you're using latest paru version
- Clear cache: `paru -Sc`
- Check disk space: `df -h`
- Verify it's actually paru: `which paru`

---

## Best Practices

1. **Use as default**
   ```python
   # Let factory choose paru automatically
   pm = PackageManagerFactory.create_auto()
   ```

2. **Keep paru updated**
   ```bash
   paru -S paru  # Update paru itself
   ```

3. **Install base-devel**
   ```bash
   sudo pacman -S base-devel  # Required for AUR
   ```

4. **Clear cache periodically**
   ```bash
   paru -Sc  # Clear package cache
   ```

---

## See Also

- [Pacman Implementation](pacman.md) - Official package manager
- [Yay Implementation](yay.md) - Alternative AUR helper
- [API Reference](../api_reference.md) - Complete API documentation
- [Usage Guide](../usage_guide.md) - Usage patterns and examples

---

**Official Repository:** https://github.com/Morganamilo/paru
**AUR Page:** https://aur.archlinux.org/packages/paru
**Documentation:** https://github.com/Morganamilo/paru/wiki
