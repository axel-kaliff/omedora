# keyd.spec — system-wide key remapping daemon (pneuma EL10 addition).
#
# Not packaged in Fedora or EPEL; the community COPR (alternateved/keyd) has no
# epel-10 chroot, so pneuma vendors a minimal spec. Mirrors the from-source
# recipe previously in pneuma's build/10-build.sh: the Makefile only installs
# keyd.service when systemd is *running* (never true in mock), so the generated
# unit is installed explicitly; the Makefile's `groupadd keyd` is replaced by a
# sysusers.d fragment per packaging guidelines.
Name:           keyd
Version:        2.5.0
Release:        1%{?dist}
Summary:        System-wide key remapping daemon at the evdev layer
License:        MIT
URL:            https://github.com/rvaiya/keyd
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        keyd.sysusers

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
# keyd-application-mapper is a python script
Requires:       python3

%description
keyd is a key remapping daemon that operates at the evdev layer, so remappings
apply in every environment: Wayland compositors, X11, and virtual consoles
alike. Configuration lives in /etc/keyd/.

%prep
%autosetup

%build
%set_build_flags
# The version banner shells out to `git describe`; there is no repo in the
# build root, so the commit part is simply empty — harmless.
%make_build PREFIX=%{_prefix}

%install
%make_install PREFIX=%{_prefix}
# Makefile skips the unit unless systemd is running (never true in mock)
install -Dm644 keyd.service %{buildroot}%{_unitdir}/keyd.service
install -Dm644 %{SOURCE1} %{buildroot}%{_sysusersdir}/keyd.conf

%files
%license LICENSE
%dir %{_sysconfdir}/keyd
%{_bindir}/keyd
%{_bindir}/keyd-application-mapper
%{_unitdir}/keyd.service
%{_sysusersdir}/keyd.conf
%{_datadir}/keyd/
%{_docdir}/keyd/
%{_mandir}/man1/keyd.1.gz
%{_mandir}/man1/keyd-application-mapper.1.gz

%changelog
* Sun Aug 17 2026 pneuma <noreply@pneuma> - 2.5.0-1
- Initial EL10 packaging for the pneuma image (previously compiled in-image).
