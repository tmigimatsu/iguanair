%define pyver %(python -V 2>&1 | sed 's/Python \\(.\\..\\).*/\\1/')
%define pydir /usr/lib/python%{pyver}/site-packages
%define uid   213

# some features can be disabled during the rpm build
%{?_without_clock_gettime: %define _disable_clock_gettime --disable-clock_gettime}

Name:           iguanaIR
Version:        0.93
Release:        1
Summary:        Driver for Iguanaworks USB IR transceiver.

Group:          System Environment/Daemons
License:        GPL
URL:            http://iguanaworks.net/ir
Source0:        http://iguanaworks.net/ir/releases/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
PreReq:         /sbin/chkconfig, /sbin/service
Requires:       libusb >= 0.1.10 lirc >= 0.8.1

%description
This package provides igdaemon and igclient, the programs necessary to
control the Iguanaworks USB IR transceiver.  The header files needed
to interact with igdaemon are also included.

%package python
Group: System Environment/Daemons
Summary: Python module for Iguanaworks USB IR transceiver.
Requires: python >= 2.4 iguanaIR = %{version} /usr/bin/install /usr/sbin/useradd /usr/sbin/userdel /sbin/chkconfig
BuildRequires: python-devel swig

%description python
This package provides the swig-generated Python module for interfacing
with the Iguanaworks USB IR transceiver.

%prep
%setup -q


%build
echo %{?_disable_clock_gettime}
%configure %{?_disable_clock_gettime}
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install PREFIX=$RPM_BUILD_ROOT/usr DESTDIR=$RPM_BUILD_ROOT INLIBDIR=$RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{pydir}
install _iguanaIR.so $RPM_BUILD_ROOT%{pydir}
install iguanaIR.py $RPM_BUILD_ROOT%{pydir}


%clean
rm -rf $RPM_BUILD_ROOT

# must create the user and group before files are put down
%pre
#TODO: stupid to not support the long versions
/usr/sbin/useradd -u %{uid} -c "Iguanaworks IR Daemon" -d / -s /sbin/nologin iguanair 2>/dev/null || true
#/usr/sbin/useradd --uid %{uid} --comment "Iguanaworks IR Daemon" --home / --shell /sbin/nologin iguanair 2>/dev/null || true

# must add the service after the files are placed
%post
/sbin/chkconfig --add %{name}
/usr/bin/install --mode=755 --owner=iguanair --group=iguanair -d /dev/iguanaIR

# before the files are removed stop the service
%preun
if [ $1 = 0 ]; then
        /sbin/service %{name} stop > /dev/null 2>&1 || true
        /sbin/chkconfig --del %{name}
        /bin/rmdir /dev/iguanaIR 2>/dev/null || true
fi

# after the files are removed nuke the user and group
%postun
if [ $1 = 0 ]; then
        /usr/sbin/userdel iguanair
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE WHY protocols.txt README.txt notes.txt
/usr/bin/*
%{_libdir}/lib%{name}.so
/etc/init.d/%{name}
%config /etc/default/%{name}
# TODO: autoconf must decide!
/etc/udev/rules.d/%{name}.rules
%attr(755, iguanair, iguanair) /etc/udev/devices/%{name}
# This is for fairly old versions of Fedora....
#/etc/hotplug/usb/%{name}*
/usr/include/%{name}.h

%files python
%{pydir}/*
# TODO: autoconf needed!
#%ghost %{pydir}/*.pyo

%changelog
* Sat Mar 10 2007 Joseph Dunn <jdunn@iguanaworks.net> 0.31-1
- First release with tentative win32 and darwin support.  Darwin needs
  some work, and windows needs to interface with applications.

* Thu Feb 1 2007 Joseph Dunn <jdunn@iguanaworks.net> 0.30-1
- Added a utility to change the frequency on firmware version 3, and
  had to make iguanaRemoveData accessible to python code.

* Sun Jan 21 2007 Joseph Dunn <jdunn@iguanaworks.net> 0.29-1
- Last currently known problem in the driver.  Using clock_gettime
  instead of gettimeofday to avoid clock rollbacks.

* Sun Dec 31 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.26-1
- Happy New Years! and a bugfix.  Long standing bug that caused the
  igdaemon to hang is fixed.

* Sun Dec 10 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.25-1
- The socket specification accept a path instead of just an index or
  label.

* Wed Dec 6 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.24-1
- Fixes bad argument parsing in igdaemon, and the init script *should*
  work for fedora and debian now.

* Wed Oct 18 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.19-1
- A real release has been made, and we'll try to keep track of version
  numbers a bit better now.

* Sat Sep 23 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.10-1
- Preparing for a real release.

* Wed Jul 11 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.9-1
- Switch to using udev instead of hotplug.

* Mon Jul 10 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.8-1
- Version number bumps, and added python support and package.

* Mon Mar 27 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.5-1
- Version number bump.

* Mon Mar 20 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.4-1
- Version number bump.

* Tue Mar 07 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.3-1
- Packaged a client library, and header file.

* Tue Mar 07 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.2-2
- Added support for chkconfig

* Tue Mar 07 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.2-1
- Added files for hotplug.

* Tue Mar 07 2006 Joseph Dunn <jdunn@iguanaworks.net> 0.1-1
- Initial RPM spec file.