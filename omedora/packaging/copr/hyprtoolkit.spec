# hyprtoolkit.spec — modern C++ Wayland-native GUI toolkit (omedora).
#
# Underpins hyprland-guiutils (the new hyprtoolkit-based GUI path). Not in
# Fedora 44. Adapted from solopasha/hyprlandRPM. omedora conventions: pinned
# Version, explicit Release + changelog, soname via glob.

Name:           hyprtoolkit
Version:        0.5.4
Release:        2%{?dist}
Summary:        A modern C++ Wayland-native GUI toolkit

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprtoolkit
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  cmake(hyprwayland-scanner)
BuildRequires:  gcc-c++
%if 0%{?rhel} >= 10
# EL10: the hypr 0.56 stack needs C++26 library features missing from the base
# gcc 14 libstdc++; gcc-toolset-15 links them statically via libstdc++_nonshared
# so the built binaries run on the stock EL10 runtime. The matching annobin
# plugin lets the distro's default -fplugin=annobin flags load under gcc 15.
BuildRequires:  gcc-toolset-15-gcc-c++
BuildRequires:  gcc-toolset-15-binutils
BuildRequires:  gcc-toolset-15-gcc-plugin-annobin
%endif
BuildRequires:  mesa-libEGL-devel
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(aquamarine)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hyprgraphics)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
%if 0%{?rhel} >= 10
# EL10's iniparser-devel (4.1, CRB) ships headers and library but no .pc file;
# a minimal pkg-config shim is generated in %%build so CMake still finds it.
BuildRequires:  iniparser-devel
%else
BuildRequires:  pkgconfig(iniparser)
%endif
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(aquamarine)
Requires:       pkgconfig(cairo)
Requires:       pkgconfig(hyprgraphics)
%description    devel
Development files for %{name}.

%prep
%autosetup -p1

%build
%if 0%{?rhel} >= 10
export PATH=/opt/rh/gcc-toolset-15/root/usr/bin:${PATH}
%endif
%if 0%{?rhel} >= 10
mkdir -p %{_builddir}/el10-pc-shim
cat > %{_builddir}/el10-pc-shim/iniparser.pc <<'INIPC'
Name: iniparser
Description: INI file parser (shim for EL10 iniparser-devel, which has no .pc)
Version: 4.1
Libs: -liniparser
Cflags: -I%{_includedir}/iniparser
INIPC
export PKG_CONFIG_PATH="%{_builddir}/el10-pc-shim${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
%endif
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Mon Aug 03 2026 omedora <noreply@omedora> - 0.5.4-2
- Rebuild against hyprutils 0.14.0 and aquamarine 0.14.0 (both SONAME 13).

* Sat May 30 2026 omedora <noreply@omedora> - 0.5.4-1
- Initial omedora build of hyprtoolkit 0.5.4 (adapted from solopasha/hyprlandRPM).
