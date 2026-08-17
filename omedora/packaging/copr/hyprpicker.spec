# hyprpicker.spec — wlroots-compatible Wayland color picker (omedora).
#
# Adapted from solopasha/hyprlandRPM. omedora conventions: pinned Version,
# explicit Release + changelog.

Name:           hyprpicker
Version:        0.4.7
Release:        2%{?dist}
Summary:        A wlroots-compatible Wayland color picker
# LICENSE: BSD-3-Clause; bundled wlr-layer-shell XML: HPND-sell-variant
License:        BSD-3-Clause AND HPND-sell-variant
URL:            https://github.com/hyprwm/hyprpicker
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
%if 0%{?rhel} >= 10
# EL10: the hypr 0.56 stack needs C++26 library features missing from the base
# gcc 14 libstdc++; gcc-toolset-15 links them statically via libstdc++_nonshared
# so the built binaries run on the stock EL10 runtime. The matching annobin
# plugin lets the distro's default -fplugin=annobin flags load under gcc 15.
BuildRequires:  gcc-toolset-15-gcc-c++
BuildRequires:  gcc-toolset-15-gcc-plugin-annobin
%endif

BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(hyprutils) >= 0.14.0
BuildRequires:  pkgconfig(hyprwayland-scanner) >= 0.4.6
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)

Recommends:     wl-clipboard

%description
%{summary}.

%prep
%autosetup -p1

%build
%if 0%{?rhel} >= 10
. /opt/rh/gcc-toolset-15/enable
%endif
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_MANDIR=%{_mandir}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.*

%changelog
* Mon Aug 03 2026 omedora <noreply@omedora> - 0.4.7-2
- Rebuild against hyprutils 0.14.0 (libhyprutils SONAME 12 -> 13).

* Sat May 30 2026 omedora <noreply@omedora> - 0.4.7-1
- Initial omedora build of hyprpicker 0.4.7 (adapted from solopasha/hyprlandRPM).
