# hyprsunset.spec — blue-light filter for Hyprland (omedora).
#
# Adapted from solopasha/hyprlandRPM. omedora conventions: pinned Version,
# explicit Release + changelog.

Name:           hyprsunset
Version:        0.4.0
Release:        1%{?dist}
Summary:        An application to enable a blue-light filter on Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsunset
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
BuildRequires:  systemd-rpm-macros

BuildRequires:  pkgconfig(hyprland-protocols)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(hyprwayland-scanner)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%description
%{summary}.

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

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service

%changelog
* Mon Aug 03 2026 omedora <noreply@omedora> - 0.4.0-1
- Update to hyprsunset 0.4.0 (Hyprland 0.56.1 wave).
- Rebuilt against hyprutils 0.14.0 (SONAME 13).

* Sat May 30 2026 omedora <noreply@omedora> - 0.3.3-1
- Initial omedora build of hyprsunset 0.3.3 (adapted from solopasha/hyprlandRPM).
