# aquamarine.spec — light Linux rendering/backend library for Hyprland (omedora).
#
# Hyprland's rendering backend. 0.15.1 (the version Omarchy stable ships)
# exports libaquamarine.so.14, so hyprland, hypxrland and hyprtoolkit are
# rebuilt with it in the same wave. Not in Fedora 44. Adapted from
# solopasha/hyprlandRPM. omedora conventions: pinned Version, explicit Release +
# changelog, soname via glob.

Name:           aquamarine
Version:        0.15.1
Release:        1%{?dist}
Summary:        A very light linux rendering backend library

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/aquamarine
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  cmake
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

BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  pkgconfig(hyprutils) >= 0.14.2
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.6
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
%{summary}.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
Development files for %{name}.

%prep
%autosetup -p1

%build
%if 0%{?rhel} >= 10
export PATH=/opt/rh/gcc-toolset-15/root/usr/bin:${PATH}
%endif
%cmake -DCMAKE_BUILD_TYPE=Release
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
* Wed Nov 18 2026 omedora <noreply@omedora> - 0.15.1-1
- Update to aquamarine 0.15.1, the version Omarchy stable ships.
- SONAME 13 -> 14: hyprland, hypxrland and hyprtoolkit are rebuilt in the
  same wave.

* Mon Aug 03 2026 omedora <noreply@omedora> - 0.14.0-1
- Update to aquamarine 0.14.0, the ABI pair for Hyprland 0.56.1.
- Exports libaquamarine.so.13; rebuilt against hyprutils 0.14.0.

* Tue Jun 16 2026 omedora <noreply@omedora> - 0.12.1-1
- Bump to upstream 0.12.1 (part of the Hyprland 0.55.4 wave; SONAME unchanged).

* Sat May 30 2026 omedora <noreply@omedora> - 0.12.0-1
- Initial omedora build of aquamarine 0.12.0 (adapted from solopasha/hyprlandRPM).
- Exports libaquamarine.so.11, matching Hyprland 0.55.2.
