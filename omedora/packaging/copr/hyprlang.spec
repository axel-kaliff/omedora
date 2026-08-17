# hyprlang.spec — implementation library for the hypr config language (omedora).
#
# BuildRequires hyprutils-devel — this is the canonical 2-spec chain that proves
# build-local.sh resolves a just-built sibling from the local /copr/repo. Fedora
# 44 ships a stale 0.6.4; omedora vendors 0.6.8 (newer EVR ⇒ auto-upgrade).
# Adapted from solopasha/hyprlandRPM. omedora conventions: pinned Version,
# explicit Release + changelog, soname via glob.

Name:           hyprlang
Version:        0.6.8
Release:        2%{?dist}
Summary:        The official implementation library for the hypr config language

License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
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
BuildRequires:  pkgconfig(hyprutils) >= 0.14.0

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
%cmake
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprlang.so.*

%files devel
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
* Mon Aug 03 2026 omedora <noreply@omedora> - 0.6.8-2
- Rebuild against hyprutils 0.14.0 (libhyprutils SONAME 12 -> 13).

* Sat May 30 2026 omedora <noreply@omedora> - 0.6.8-1
- Initial omedora build of hyprlang 0.6.8 (adapted from solopasha/hyprlandRPM).
- Out-versions Fedora's stale 0.6.4.
