"""Tests for package manager types and enums."""

from dotfiles_package_manager.core.types import (
    DistributionFamily,
    InstallResult,
    PackageInfo,
    PackageManagerType,
    SearchResult,
)


class TestDistributionFamily:
    """Tests for DistributionFamily enum."""

    def test_distribution_family_values(self):
        """Test that all distribution families have correct values."""
        assert DistributionFamily.ARCH.value == "arch"
        assert DistributionFamily.DEBIAN.value == "debian"
        assert DistributionFamily.REDHAT.value == "redhat"
        assert DistributionFamily.UNKNOWN.value == "unknown"

    def test_distribution_family_members(self):
        """Test that all expected distribution families exist."""
        families = list(DistributionFamily)
        assert len(families) == 4
        assert DistributionFamily.ARCH in families
        assert DistributionFamily.DEBIAN in families
        assert DistributionFamily.REDHAT in families
        assert DistributionFamily.UNKNOWN in families


class TestPackageManagerType:
    """Tests for PackageManagerType enum."""

    def test_package_manager_type_values(self):
        """Test that all package manager types have correct values."""
        assert PackageManagerType.PACMAN.value == "pacman"
        assert PackageManagerType.YAY.value == "yay"
        assert PackageManagerType.PARU.value == "paru"
        assert PackageManagerType.APT.value == "apt"
        assert PackageManagerType.APT_GET.value == "apt-get"
        assert PackageManagerType.DNF.value == "dnf"
        assert PackageManagerType.YUM.value == "yum"

    def test_distribution_family_property_arch(self):
        """Test distribution_family property for Arch managers."""
        assert (
            PackageManagerType.PACMAN.distribution_family
            == DistributionFamily.ARCH
        )
        assert (
            PackageManagerType.YAY.distribution_family
            == DistributionFamily.ARCH
        )
        assert (
            PackageManagerType.PARU.distribution_family
            == DistributionFamily.ARCH
        )

    def test_distribution_family_property_debian(self):
        """Test distribution_family property for Debian managers."""
        assert (
            PackageManagerType.APT.distribution_family
            == DistributionFamily.DEBIAN
        )
        assert (
            PackageManagerType.APT_GET.distribution_family
            == DistributionFamily.DEBIAN
        )

    def test_distribution_family_property_redhat(self):
        """Test distribution_family property for RedHat managers."""
        assert (
            PackageManagerType.DNF.distribution_family
            == DistributionFamily.REDHAT
        )
        assert (
            PackageManagerType.YUM.distribution_family
            == DistributionFamily.REDHAT
        )

    def test_is_third_party_helper_true(self):
        """Test is_third_party_helper for AUR helpers."""
        assert PackageManagerType.YAY.is_third_party_helper is True
        assert PackageManagerType.PARU.is_third_party_helper is True

    def test_is_third_party_helper_false(self):
        """Test is_third_party_helper for official managers."""
        assert PackageManagerType.PACMAN.is_third_party_helper is False
        assert PackageManagerType.APT.is_third_party_helper is False
        assert PackageManagerType.DNF.is_third_party_helper is False

    def test_requires_sudo_true(self):
        """Test requires_sudo for managers that need sudo."""
        assert PackageManagerType.PACMAN.requires_sudo is True
        assert PackageManagerType.APT.requires_sudo is True
        assert PackageManagerType.DNF.requires_sudo is True

    def test_requires_sudo_false(self):
        """Test requires_sudo for AUR helpers (handle sudo internally)."""
        assert PackageManagerType.YAY.requires_sudo is False
        assert PackageManagerType.PARU.requires_sudo is False


class TestPackageInfo:
    """Tests for PackageInfo dataclass."""

    def test_package_info_creation_minimal(self):
        """Test creating PackageInfo with minimal fields."""
        info = PackageInfo(name="test-package")
        assert info.name == "test-package"
        assert info.version is None
        assert info.description is None
        assert info.repository is None
        assert info.installed is False
        assert info.size is None
        assert info.dependencies == []

    def test_package_info_creation_full(self):
        """Test creating PackageInfo with all fields."""
        info = PackageInfo(
            name="test-package",
            version="1.0.0",
            description="A test package",
            repository="core",
            installed=True,
            size="1.5 MB",
            dependencies=["dep1", "dep2"],
        )
        assert info.name == "test-package"
        assert info.version == "1.0.0"
        assert info.description == "A test package"
        assert info.repository == "core"
        assert info.installed is True
        assert info.size == "1.5 MB"
        assert info.dependencies == ["dep1", "dep2"]

    def test_package_info_dependencies_default(self):
        """Test that dependencies defaults to empty list."""
        info = PackageInfo(name="test")
        assert info.dependencies == []
        assert isinstance(info.dependencies, list)

    def test_package_info_dependencies_none_converted(self):
        """Test that None dependencies is converted to empty list."""
        info = PackageInfo(name="test", dependencies=None)
        assert info.dependencies == []


class TestInstallResult:
    """Tests for InstallResult dataclass."""

    def test_install_result_creation_minimal(self):
        """Test creating InstallResult with minimal fields."""
        result = InstallResult(success=True)
        assert result.success is True
        assert result.packages_installed == []
        assert result.packages_failed == []
        assert result.output == ""
        assert result.error_message is None

    def test_install_result_creation_full(self):
        """Test creating InstallResult with all fields."""
        result = InstallResult(
            success=True,
            packages_installed=["pkg1", "pkg2"],
            packages_failed=["pkg3"],
            output="Installation output",
            error_message="Some warning",
        )
        assert result.success is True
        assert result.packages_installed == ["pkg1", "pkg2"]
        assert result.packages_failed == ["pkg3"]
        assert result.output == "Installation output"
        assert result.error_message == "Some warning"

    def test_install_result_success_true(self):
        """Test successful installation result."""
        result = InstallResult(
            success=True,
            packages_installed=["package1"],
            packages_failed=[],
        )
        assert result.success is True
        assert len(result.packages_installed) == 1
        assert len(result.packages_failed) == 0

    def test_install_result_success_false(self):
        """Test failed installation result."""
        result = InstallResult(
            success=False,
            packages_installed=[],
            packages_failed=["package1"],
            error_message="Installation failed",
        )
        assert result.success is False
        assert len(result.packages_installed) == 0
        assert len(result.packages_failed) == 1
        assert result.error_message is not None

    def test_install_result_lists_default(self):
        """Test that package lists default to empty."""
        result = InstallResult(success=True)
        assert result.packages_installed == []
        assert result.packages_failed == []

    def test_install_result_none_converted(self):
        """Test that None lists are converted to empty lists."""
        result = InstallResult(
            success=True,
            packages_installed=None,
            packages_failed=None,
        )
        assert result.packages_installed == []
        assert result.packages_failed == []


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_search_result_creation_minimal(self):
        """Test creating SearchResult with minimal fields."""
        result = SearchResult()
        assert result.packages == []
        assert result.query == ""
        assert result.total_found == 0

    def test_search_result_creation_full(self):
        """Test creating SearchResult with all fields."""
        packages = [
            PackageInfo(name="pkg1", version="1.0.0"),
            PackageInfo(name="pkg2", version="2.0.0"),
        ]
        result = SearchResult(
            packages=packages,
            query="test",
            total_found=2,
        )
        assert len(result.packages) == 2
        assert result.query == "test"
        assert result.total_found == 2

    def test_search_result_total_found_auto_calculated(self):
        """Test that total_found is auto-calculated from packages list."""
        packages = [
            PackageInfo(name="pkg1"),
            PackageInfo(name="pkg2"),
            PackageInfo(name="pkg3"),
        ]
        result = SearchResult(packages=packages, query="test")
        assert result.total_found == 3

    def test_search_result_total_found_explicit(self):
        """Test that explicit total_found is preserved."""
        packages = [PackageInfo(name="pkg1")]
        result = SearchResult(packages=packages, query="test", total_found=100)
        assert result.total_found == 100  # Explicit value, not auto-calculated

    def test_search_result_empty(self):
        """Test empty search result."""
        result = SearchResult(query="nonexistent")
        assert result.packages == []
        assert result.total_found == 0

    def test_search_result_none_converted(self):
        """Test that None packages is converted to empty list."""
        result = SearchResult(packages=None, query="test")
        assert result.packages == []
        assert result.total_found == 0
