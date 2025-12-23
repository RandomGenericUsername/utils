# Answers to the 6 Mandatory Questions

Based on analysis of the `dotfiles-package-manager` library and its real-world usage in `dotfiles-installer`.

---

## Question 1: What is the system boundary to test first?

**Answer**: The **PackageManager abstract class** and **PackageManagerFactory** are the primary boundaries.

**Evidence from Real Usage**:
- `dotfiles-installer/src/pipeline_steps/package_management_steps.py` uses:
  - `PackageManagerFactory.create_auto(prefer_third_party=True)` (line 60-62)
  - `PackageManagerFactory.get_available_managers()` (line 73-76)
  - `PackageManager.update_system(dry_run)` (line 140)
  - `PackageManager.install(packages, update_system=False)` (line 260)

**Consuming Application**: Yes, the library is consumed by `dotfiles-installer`, a pipeline-based dotfiles installation system.

**Primary Boundary**:
1. **PackageManagerFactory** - Entry point for creating managers
2. **PackageManager abstract class** - Public API for all operations

---

## Question 2: Current vs Intended Behavior for Ambiguous Cases

**Approach**: **Freeze current behavior first** (characterization tests), then define desired behavior, then plan migration.

### Ambiguous Case 1: Partial Install Failures
**Current Behavior**: `success=True` if ANY package succeeds  
**Evidence**: `pacman.py:128` - `success=len(successful_packages) > 0`

**Decision**: ✅ **Freeze this behavior** - it's intentional and used in production

---

### Ambiguous Case 2: Sudo Authentication Failure
**Current Behavior**: Raises `PackageManagerError`  
**Evidence**: `base.py:170-177` - subprocess errors propagate as PackageManagerError

**Decision**: ✅ **Freeze this behavior** - pipeline handles it gracefully (`package_management_steps.py:282-286`)

---

### Ambiguous Case 3: Removing Non-Existent Packages
**Current Behavior**: Varies by manager (pacman fails, apt succeeds)  
**Evidence**: Different exit codes from underlying tools

**Decision**: ⚠️ **Characterize current behavior**, then decide if consistency is needed

---

### Ambiguous Case 4: Dry-Run Output Format
**Current Behavior**: Varies by manager  
**Evidence**: `pacman.py:170` uses `-Qu`, `apt.py` would use different command

**Decision**: ⚠️ **Characterize current behavior** - output is logged but not parsed

---

## Question 3: Top 3 Critical Flows

Based on real usage in `dotfiles-installer`:

### Flow 1: Auto-Detect & Create Manager (MOST CRITICAL)
**Entry**: `PackageManagerFactory.create_auto(prefer_third_party=True)`  
**Evidence**: `package_management_steps.py:60-62` - First step in pipeline  
**Why Critical**: If this fails, entire installation fails

---

### Flow 2: Update System Before Install
**Entry**: `update_system(dry_run=False)` → `install(packages, update_system=False)`  
**Evidence**: `package_management_steps.py:140-145` then `260`  
**Why Critical**: Prevents partial upgrades on Arch (can break system)

---

### Flow 3: Install with Partial Failure Tracking
**Entry**: `install(packages)` with some packages failing  
**Evidence**: `package_management_steps.py:260-280` - Tracks `packages_installed` and `packages_failed`  
**Why Critical**: Pipeline must continue even if some packages fail

---

### Additional Critical Flows (Beyond Top 3):

**Flow 4**: Cross-Manager Consistency (USER REQUIREMENT #5 - HIGHEST PRIORITY)  
**Flow 5**: Get Available Managers (debugging/logging)  
**Flow 6**: Error Handling (PackageManagerError must be catchable)  
**Flow 7**: Dry-Run Mode (check updates without applying)  
**Flow 8**: Empty Package Lists (common edge case)

---

## Question 4: Which Dependencies to Mock vs Run Real?

**Answer**: **Mock everything** - no real package manager execution needed.

**Mocking Strategy**:
- ✅ Mock `subprocess.run()` for all command execution
- ✅ Mock `shutil.which()` for availability checks
- ✅ Mock `/etc/os-release` file reads for distribution detection
- ✅ Mock `Path.exists()` for executable checks

**Rationale**: User confirmed mocking is sufficient (answer #4)

---

## Question 5: Out of Scope Areas

**CRITICAL CORRECTION**: Testing ALL 5 package managers is **IN SCOPE** and **HIGHEST PRIORITY**.

### IN SCOPE (CRITICAL):
- ✅ Testing ALL package managers (pacman, yay, paru, apt, dnf)
- ✅ Cross-manager consistency (same behavior for same inputs)
- ✅ All distribution families (Arch, Debian, RedHat)

### OUT OF SCOPE:
- ❌ Testing all package manager **versions** (e.g., pacman 6.0 vs 6.1)
- ❌ Testing all distro **variants** (e.g., every Ubuntu version)
- ❌ Network failures during package downloads
- ❌ Disk space exhaustion scenarios
- ❌ Performance/benchmarking tests
- ❌ Real package installation on dev machines

---

## Question 6: Stable Contracts vs Internal Interfaces

### Stable Public Contracts (MUST NOT CHANGE):

#### Factory Methods:
- `PackageManagerFactory.create_auto(prefer_third_party, distribution_family)` → `PackageManager`
- `PackageManagerFactory.create(manager_type)` → `PackageManager`
- `PackageManagerFactory.get_available_managers()` → `list[PackageManagerType]`
- `PackageManagerFactory.get_recommended_manager(distribution_family)` → `PackageManagerType | None`
- `PackageManagerFactory.create_recommended(distribution_family)` → `PackageManager`
- `PackageManagerFactory.is_available(manager_type)` → `bool`

#### PackageManager Methods:
- `install(packages, update_system)` → `InstallResult`
- `remove(packages, remove_dependencies)` → `InstallResult`
- `search(query)` → `SearchResult`
- `update_system(dry_run)` → `InstallResult`
- `is_installed(package)` → `bool`
- `get_package_info(package)` → `PackageInfo | None`

#### Module-Level Functions:
- `detect_distribution_family()` → `DistributionFamily`

#### Data Types (Dataclasses):
- `PackageInfo` (fields: name, version, description, repository, installed, size, dependencies)
- `InstallResult` (fields: success, packages_installed, packages_failed, output, error_message)
- `SearchResult` (fields: packages, query, total_found)

#### Enums:
- `PackageManagerType` (values: PACMAN, YAY, PARU, APT, DNF)
- `DistributionFamily` (values: ARCH, DEBIAN, REDHAT, UNKNOWN)

#### Exceptions:
- `PackageManagerError` (raised for all package manager failures)

#### Preference Orders (MUST REMAIN STABLE):
- Arch (with third-party): paru → yay → pacman
- Arch (without third-party): pacman only
- Debian: apt only
- RedHat: dnf only

---

### Internal Interfaces (CAN CHANGE):
- `_parse_*` methods in base classes
- `_run_command` implementations
- `_find_executable` implementations
- Specific command-line flags used
- Output parsing logic
- `_is_available` (private method)

---

## Summary

1. **System Boundary**: PackageManager + PackageManagerFactory (used by dotfiles-installer)
2. **Behavior**: Freeze current behavior with characterization tests, then define desired behavior
3. **Critical Flows**: 8 flows identified, with cross-manager consistency as HIGHEST PRIORITY
4. **Mocking**: Mock everything (subprocess, shutil, file reads)
5. **Scope**: Testing ALL 5 managers is CRITICAL (not out of scope)
6. **Contracts**: 6 factory methods, 6 package manager methods, 3 data types, 2 enums, 1 exception, 1 function

**Next Step**: Write characterization tests, then cross-manager contract tests.

