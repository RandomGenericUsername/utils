# Troubleshooting

Common issues and solutions for the `dotfiles_package_manager` module.

---

## Table of Contents

1. [Arch Linux Specific Issues](#arch-linux-specific-issues)
2. [Installation Issues](#installation-issues)
3. [Permission Issues](#permission-issues)
4. [Package Issues](#package-issues)
5. [Search Issues](#search-issues)
6. [Factory Issues](#factory-issues)
7. [Performance Issues](#performance-issues)
8. [Debugging Tips](#debugging-tips)

---

## Arch Linux Specific Issues

### Issue: Partial Upgrade / Dependency Breakage

**Symptoms:**
```
error while loading shared libraries: libfoo.so.X: cannot open shared object file
```
or
```
error: failed to prepare transaction (could not satisfy dependencies)
:: package-name: requires libfoo.so.X but libfoo.so.Y is installed
```

**Causes:**
- Using `-Sy` without `-u` (partial upgrade)
- Installing packages without upgrading the system first
- Mixing packages from different repository states

**Why This Happens:**

Arch Linux is a **rolling release** distribution. When you sync package databases (`-Sy`) without upgrading (`-u`), you can install packages that depend on newer library versions than what's currently installed on your system.

**Example:**
```bash
# ❌ WRONG - Causes partial upgrade
yay -Sy thunderbird

# What happens:
# 1. Syncs repos (sees thunderbird needs libvpx.so.9)
# 2. Installs thunderbird with libvpx.so.9
# 3. Does NOT upgrade existing packages (ffmpeg still uses libvpx.so.8)
# 4. Result: ffmpeg breaks because libvpx.so.8 is gone
```

**Solutions:**

1. **Always use full system upgrade:**
   ```python
   # This module automatically prevents partial upgrades
   pm = PackageManagerFactory.create_auto()

   # Option 1: Upgrade system first
   pm.update_system()  # Uses -Syu
   pm.install(["thunderbird"])  # Uses -S only

   # Option 2: Use update_system flag
   pm.install(["thunderbird"], update_system=True)  # Runs -Syu first
   ```

2. **Manual fix if already broken:**
   ```bash
   # Full system upgrade to fix dependencies
   yay -Syu

   # If that fails, force database sync and upgrade
   yay -Syyu
   ```

3. **Prevention:**
   - Never use `yay -Sy package` or `pacman -Sy package`
   - Always use `yay -Syu` or `yay -Syu package`
   - Let this module handle it (it prevents partial upgrades automatically)

**See Also:**
- [Arch Linux Partial Upgrades Documentation](arch-partial-upgrades.md)
- [Arch Wiki: System Maintenance](https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported)

---

## Installation Issues

### Issue: PackageManagerError - Executable not found

**Symptoms:**
```
PackageManagerError: Package manager executable not found: pacman
```

**Causes:**
- Package manager not installed
- Package manager not in PATH
- Running on non-Arch system

**Solutions:**

1. **Install the package manager:**
   ```bash
   # For pacman (should be pre-installed on Arch)
   # If missing, reinstall Arch Linux

   # For yay
   git clone https://aur.archlinux.org/yay.git
   cd yay && makepkg -si

   # For paru
   git clone https://aur.archlinux.org/paru.git
   cd paru && makepkg -si
   ```

2. **Check PATH:**
   ```bash
   which pacman
   which yay
   which paru
   echo $PATH
   ```

3. **Use specific manager if available:**
   ```python
   # Check what's available
   available = PackageManagerFactory.get_available_managers()
   print(f"Available: {[m.value for m in available]}")

   # Use first available
   if available:
       pm = PackageManagerFactory.create(available[0])
   ```

---

### Issue: Installation fails silently

**Symptoms:**
```python
result = pm.install(["package"])
# result.success is False, but no error message
```

**Causes:**
- Package doesn't exist
- Network issues
- Repository not synchronized

**Solutions:**

1. **Check error message:**
   ```python
   if not result.success:
       print(f"Error: {result.error_message}")
       print(f"Output: {result.output}")
   ```

2. **Sync repositories first:**
   ```python
   pm.update_system(dry_run=False)
   result = pm.install(["package"])
   ```

3. **Search for package first:**
   ```python
   search_result = pm.search("package")
   if search_result.packages:
       exact_name = search_result.packages[0].name
       result = pm.install([exact_name])
   ```

---

### Issue: Partial installation success

**Symptoms:**
```python
result = pm.install(["pkg1", "pkg2", "pkg3"])
# result.success is False
# result.packages_installed = ["pkg1", "pkg2"]
# result.packages_failed = ["pkg3"]
```

**Causes:**
- Some packages don't exist
- Dependency conflicts
- Network issues for specific packages

**Solutions:**

1. **Check which packages failed:**
   ```python
   if result.packages_failed:
       for pkg in result.packages_failed:
           info = pm.get_package_info(pkg)
           if not info:
               print(f"{pkg} not found in repositories")
   ```

2. **Install failed packages separately:**
   ```python
   for pkg in result.packages_failed:
       single_result = pm.install([pkg])
       if not single_result.success:
           print(f"Failed to install {pkg}: {single_result.error_message}")
   ```

3. **Search for correct package names:**
   ```python
   for pkg in result.packages_failed:
       search_result = pm.search(pkg, limit=5)
       print(f"Did you mean one of these?")
       for found_pkg in search_result.packages:
           print(f"  - {found_pkg.name}")
   ```

---

## Permission Issues

### Issue: Permission denied during installation

**Symptoms:**
```
error: you cannot perform this operation unless you are root
```

**Causes:**
- User doesn't have sudo privileges
- Sudo password not entered
- Sudo timeout expired

**Solutions:**

1. **Ensure user has sudo access:**
   ```bash
   sudo -v  # Test sudo access
   ```

2. **Add user to wheel group:**
   ```bash
   sudo usermod -aG wheel username
   # Then edit /etc/sudoers to enable wheel group
   ```

3. **Use AUR helper instead of pacman:**
   ```python
   # AUR helpers (yay/paru) handle sudo better
   pm = PackageManagerFactory.create_auto(prefer_aur_helper=True)
   ```

4. **Check sudoers configuration:**
   ```bash
   sudo visudo
   # Ensure wheel group is enabled:
   # %wheel ALL=(ALL:ALL) ALL
   ```

---

### Issue: Sudo password prompt hangs

**Symptoms:**
- Installation hangs waiting for password
- No password prompt appears

**Causes:**
- Running in non-interactive environment
- Sudo timeout expired
- Password caching disabled

**Solutions:**

1. **Pre-authenticate with sudo:**
   ```bash
   sudo -v  # Enter password once
   # Then run your Python script
   ```

2. **Use AUR helpers (they handle this better):**
   ```python
   pm = PackageManagerFactory.create(PackageManagerType.PARU)
   ```

3. **Configure sudo timeout:**
   ```bash
   sudo visudo
   # Add: Defaults timestamp_timeout=30
   ```

---

## Package Issues

### Issue: Package not found

**Symptoms:**
```python
result = pm.install(["package-name"])
# result.success is False
# result.packages_failed = ["package-name"]
```

**Causes:**
- Package name misspelled
- Package only in AUR (using pacman)
- Repository not synchronized

**Solutions:**

1. **Search for correct package name:**
   ```python
   result = pm.search("package")
   for pkg in result.packages:
       print(f"{pkg.name} - {pkg.description}")
   ```

2. **Use AUR helper for AUR packages:**
   ```python
   # Check if using pacman
   if pm.manager_type == PackageManagerType.PACMAN:
       # Try with AUR helper
       pm = PackageManagerFactory.create(PackageManagerType.PARU)
       result = pm.install(["package-name"])
   ```

3. **Sync repositories:**
   ```python
   pm.update_system(dry_run=False)
   result = pm.install(["package-name"])
   ```

4. **Check on Arch package website:**
   - Official packages: https://archlinux.org/packages/
   - AUR packages: https://aur.archlinux.org/

---

### Issue: get_package_info returns None

**Symptoms:**
```python
info = pm.get_package_info("package")
# info is None
```

**Causes:**
- Package doesn't exist
- Package name misspelled
- Not in repositories

**Solutions:**

1. **Search first to verify package exists:**
   ```python
   result = pm.search("package")
   if result.packages:
       exact_name = result.packages[0].name
       info = pm.get_package_info(exact_name)
   ```

2. **Check if installed:**
   ```python
   if pm.is_installed("package"):
       info = pm.get_package_info("package")
   else:
       print("Package not installed")
   ```

3. **Try different package name variations:**
   ```python
   variations = ["package", "package-git", "package-bin"]
   for name in variations:
       info = pm.get_package_info(name)
       if info:
           print(f"Found: {name}")
           break
   ```

---

## Search Issues

### Issue: Search returns no results

**Symptoms:**
```python
result = pm.search("package")
# result.packages is empty
# result.total_found is 0
```

**Causes:**
- Package doesn't exist
- Database not synchronized
- Typo in search query

**Solutions:**

1. **Sync database:**
   ```python
   pm.update_system(dry_run=False)
   result = pm.search("package")
   ```

2. **Try broader search:**
   ```python
   # Instead of specific name
   result = pm.search("vim")  # Not "neovim-nightly-git"
   ```

3. **Check spelling:**
   ```python
   # Try variations
   queries = ["python", "python3", "python-"]
   for query in queries:
       result = pm.search(query, limit=5)
       if result.packages:
           print(f"Found with query: {query}")
           break
   ```

---

### Issue: Search returns too many results

**Symptoms:**
```python
result = pm.search("python")
# result.total_found is 500+
```

**Solutions:**

1. **Use limit parameter:**
   ```python
   result = pm.search("python", limit=20)
   ```

2. **Use more specific query:**
   ```python
   # Instead of "python"
   result = pm.search("python-numpy")
   ```

3. **Filter results programmatically:**
   ```python
   result = pm.search("python")
   # Filter for exact matches
   exact_matches = [pkg for pkg in result.packages if "python" == pkg.name]
   ```

---

## Factory Issues

### Issue: Factory creates wrong manager

**Symptoms:**
- Wanted paru, got yay
- Wanted AUR helper, got pacman

**Causes:**
- Preferred manager not installed
- Factory preference order

**Solutions:**

1. **Check what's available:**
   ```python
   available = PackageManagerFactory.get_available_managers()
   print(f"Available: {[m.value for m in available]}")
   ```

2. **Create specific manager:**
   ```python
   if PackageManagerFactory.is_available(PackageManagerType.PARU):
       pm = PackageManagerFactory.create(PackageManagerType.PARU)
   else:
       print("Paru not available")
   ```

3. **Install preferred manager first:**
   ```bash
   # Install paru
   git clone https://aur.archlinux.org/paru.git
   cd paru && makepkg -si
   ```

---

### Issue: No package manager available

**Symptoms:**
```
PackageManagerError: No package manager available
```

**Causes:**
- Running on non-Arch system
- No package managers installed
- Package managers not in PATH

**Solutions:**

1. **Verify system:**
   ```bash
   cat /etc/os-release
   # Should show Arch Linux or derivative
   ```

2. **Install a package manager:**
   ```bash
   # Pacman should be pre-installed on Arch
   # If not, reinstall system

   # Install yay or paru
   git clone https://aur.archlinux.org/paru.git
   cd paru && makepkg -si
   ```

3. **Check PATH:**
   ```bash
   echo $PATH
   which pacman
   ```

---

## Performance Issues

### Issue: Slow package installation

**Causes:**
- Slow mirror
- Large package downloads
- Using yay instead of paru

**Solutions:**

1. **Use faster mirror:**
   ```bash
   sudo pacman-mirrors --fasttrack
   # Or manually edit /etc/pacman.d/mirrorlist
   ```

2. **Use paru instead of yay:**
   ```python
   pm = PackageManagerFactory.create(PackageManagerType.PARU)
   ```

3. **Install multiple packages at once:**
   ```python
   # Good - single command
   pm.install(["pkg1", "pkg2", "pkg3"])

   # Bad - three commands
   pm.install(["pkg1"])
   pm.install(["pkg2"])
   pm.install(["pkg3"])
   ```

---

### Issue: Slow search

**Causes:**
- Large package database
- No result limit
- Broad search query

**Solutions:**

1. **Limit results:**
   ```python
   result = pm.search("query", limit=10)
   ```

2. **Use more specific queries:**
   ```python
   # Instead of "lib"
   result = pm.search("libpython")
   ```

3. **Cache search results:**
   ```python
   # Cache for repeated searches
   search_cache = {}

   def cached_search(pm, query, limit=None):
       key = (query, limit)
       if key not in search_cache:
           search_cache[key] = pm.search(query, limit)
       return search_cache[key]
   ```

---

## Debugging Tips

### 1. Enable verbose output

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then use package manager
pm = PackageManagerFactory.create_auto()
```

---

### 2. Check command output

```python
result = pm.install(["package"])
print(f"stdout: {result.output}")
print(f"stderr: {result.error_message}")
print(f"success: {result.success}")
```

---

### 3. Test with simple operations

```python
# Test search (doesn't require sudo)
result = pm.search("vim")
print(f"Search works: {len(result.packages) > 0}")

# Test is_installed (doesn't require sudo)
installed = pm.is_installed("bash")
print(f"is_installed works: {installed}")

# Test get_package_info
info = pm.get_package_info("bash")
print(f"get_package_info works: {info is not None}")
```

---

### 4. Verify package manager works manually

```bash
# Test pacman
pacman -Ss vim

# Test yay
yay -Ss vim

# Test paru
paru -Ss vim
```

---

### 5. Check for system issues

```bash
# Check disk space
df -h

# Check network
ping archlinux.org

# Check pacman database
sudo pacman -Sy

# Check for partial upgrades
pacman -Qk
```

---

### 6. Inspect package manager state

```python
pm = PackageManagerFactory.create_auto()

print(f"Manager type: {pm.manager_type}")
print(f"Executable: {pm.executable_path}")

# Check if specific packages are available
test_packages = ["vim", "git", "nonexistent-package"]
for pkg in test_packages:
    installed = pm.is_installed(pkg)
    info = pm.get_package_info(pkg)
    print(f"{pkg}: installed={installed}, info={info is not None}")
```

---

**Next:** [Overview](overview.md) | [API Reference](api_reference.md)
