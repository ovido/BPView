Name: bpview
Version: 0.13
Release: 2%{?dist}
Summary: Business Process view for Nagios/Icinga 

Group: Applications/System
License: GPLv3+
URL: https://github.com/BPView/BPView
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: perl
BuildRequires: perl-CGI
%if "%{_vendor}" == "redhat"
%if 0%{?rhel} == 6
BuildRequires: perl-JSON
%else
# RHEL 7 and Fedora
BuildRequires: perl-JSON-PP
%endif
%endif
BuildRequires: perl-YAML-Syck
BuildRequires: perl-DBI
BuildRequires: perl-DBD-Pg
BuildRequires: selinux-policy-devel
%if 0%{?fedora} && 0%{?fedora_version} >= 21 || 0%{?rhel} >= 7
BuildRequires: systemd
%endif

Requires: httpd
Requires: memcached
Requires: mod_fcgid
Requires: perl
Requires: perl-Cache-Memcached
Requires: perl-CGI
Requires: perl-DBI
Requires: perl-DBD-MySQL
Requires: perl-DBD-Pg
Requires: perl-FCGI
Requires: perl-JSON
Requires: perl-JSON-XS
Requires: perl-Log-Log4perl
Requires: perl-Template-Toolkit
Requires: perl-Tie-IxHash
Requires: perl-Time-HiRes
Requires: perl-YAML-Syck
Requires: sudo

Requires(post):   /usr/sbin/semodule, /sbin/restorecon, /sbin/fixfiles
Requires(postun): /usr/sbin/semodule, /sbin/restorecon, /sbin/fixfiles

%define apacheuser apache
%define apachegroup apache

%global selinux_variants mls targeted

%description
BPView is the short name for Business Process View. This Tool
for Nagios and Icinga is used to display a combination of Checks
in a Business Process.

%prep
%setup -q -n %{name}-%{version}

%build
%configure --prefix=/usr \
           --sbindir=%{_libdir}/%{name} \
           --libdir=%{_libdir}/perl5/vendor_perl \
           --sysconfdir=%{_sysconfdir}/%{name} \
           --datarootdir=%{_datarootdir}/%{name} \
           --docdir=%{_docdir}/%{name}-%{version} \
           --with-web-user=%{apacheuser} \
           --with-web-group=%{apachegroup} \
           --with-web-conf=/etc/httpd/conf.d/bpview.conf

%if 0%{?fedora} && 0%{?fedora_version} >= 21 || 0%{?rhel} >= 7
cd selinux/f21
%else
cd selinux/rh6
%endif
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv %{name}.pp ../%{name}.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -

make all


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL_OPTS="" INSTALL_OPTS_WEB=""

# backup folder
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/backup

for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 selinux/%{name}.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{name}.pp
done


%clean
rm -rf $RPM_BUILD_ROOT


%post
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
    %{_datadir}/selinux/${selinuxvariant}/%{name}.pp &> /dev/null || :
done
/sbin/fixfiles -R %{name} restore || :
/usr/sbin/setsebool -P allow_ypbind=on

%postun
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
    /usr/sbin/semodule -s ${selinuxvariant} -r %{name} &> /dev/null || :
  done
  /sbin/fixfiles -R %{name} restore || :
fi


%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/%{name}/bpview.yml
%config(noreplace) %{_sysconfdir}/%{name}/bpviewd.yml
%config(noreplace) %{_sysconfdir}/%{name}/datasource.yml
%config(noreplace) %{_sysconfdir}/%{name}/mappings.yml
%config(noreplace) %{_sysconfdir}/%{name}/views
%config(noreplace) %{_sysconfdir}/%{name}/backup
%config(noreplace) %{_sysconfdir}/%{name}/bp-config
%config(noreplace) %{_sysconfdir}/httpd/conf.d/bpview.conf
%config(noreplace) %{_sysconfdir}/sudoers.d/bpview
%{_libdir}/perl5/vendor_perl
%attr(0755,root,root) %{_libdir}/%{name}/bpview.pl
%attr(0755,root,root) %{_bindir}/bpviewd
%attr(0755,root,root) %{_bindir}/bpview_reload
%attr(0775,root,apache) %{_sysconfdir}/%{name}/bp-config
%attr(0775,root,apache) %{_sysconfdir}/%{name}/views
%attr(0775,root,apache) %{_sysconfdir}/%{name}/backup
%if 0%{?fedora} && 0%{?fedora_version} >= 21 || 0%{?rhel} >= 7
%attr(0644,root,root) %{_unitdir}/bpviewd.service
%else
%attr(0775,root,root) %{_sysconfdir}/init.d/bpviewd
%endif
%{_datarootdir}/%{name}/css
%{_datarootdir}/%{name}/images
%{_datarootdir}/%{name}/javascript
%{_datarootdir}/%{name}/src
%{_datadir}/selinux/*/%{name}.pp
%attr(0755,%{apacheuser},%{apachegroup}) %{_localstatedir}/log/%{name}
%attr(0755,%{apacheuser},%{apachegroup}) %{_localstatedir}/log/%{name}/bpview.log
%doc AUTHORS ChangeLog COPYING NEWS README.md sample-config selinux



%changelog
* Fri Jun 19 2015 Rene Koch <rkoch@rk-it.at> 0.13-2
- install systemd service

* Fri Jun 19 2015 Rene Koch <rkoch@rk-it.at> 0.12.1-1
- bump to 0.12.1 maintenance release

* Mon Jun 15 2015 Rene Koch <rkoch@rk-it.at> 0.13-1
- bump to 0.13 release

* Mon Jun 15 2015 Rene Koch <rkoch@rk-it.at> 0.12-1
- bump to 0.12 release
- added mappings.yml
- removed SELinux restorecon for legacy /var/cache/bpview

* Thu Feb 26 2015 Rene Koch <rkoch@rk-it.at> 0.11-2
- compile on RHEL 7 and Fedora 21

* Fri Feb 20 2015 Rene Koch <rkoch@rk-it.at> 0.11-1
- bump to 0.11 release

* Fri Feb 13 2015 Rene Koch <rkoch@rk-it.at> 0.10.1-1
- bump to 0.10.1 release

* Thu Jan 29 2015 Rene Koch <rkoch@rk-it.at> 0.10-1
- bump to 0.10 release
- cleanup of old unused scripts
- install bpviewd.yml config file

* Wed May 14 2014 Rene Koch <rkoch@linuxland.at> 0.9.1-1
- bump to 0.9.1 bugfix release
- readded bpview_cfg_writer.pl

* Fri Apr 25 2014 Rene Koch <rkoch@linuxland.at> 0.9-2
- cleanup of old files

* Mon Apr 07 2014 Rene Koch <rkoch@linuxland.at> 0.9-1
- bump to 0.9
- Removed BuildRequires of EPEL packages
- Added bpview_reload script 

* Thu Mar 13 2014 Rene Koch <rkoch@linuxland.at> 0.8-2
- Fixed name of bpviewd init script
- Fixed permissions for /etc/bpview/backup folder

* Thu Mar 06 2014 Rene Koch <rkoch@linuxland.at> 0.8-1
- bump to 0.8
- requires perl-Proc-Daemon

* Thu Nov 21 2013 Rene Koch <r.koch@ovido.at> 0.7-2
- changed log file path to /var/log/bpview/bpview.log

* Thu Nov 21 2013 Rene Koch <r.koch@ovido.at> 0.7-1
- bump to 0.7
- added bpviewd
- requires perl-File-Pid

* Wed Nov 06 2013 Rene Koch <r.koch@ovido.at> 0.6-1
- bump to 0.6
- renamed README to README.md

* Tue Oct 29 2013 Rene Koch <r.koch@ovido.at> 0.5-1
- bump to 0.5
- removed bp-addon.cfg
- requires icinga, sudo
- /etc/sudoers.d/bpview added
- write permissions for apache on bpview/icinga config directory
- added bpview_businessprocesses.cfg
- create backup folder

* Thu Sep 5 2013 Peter Stoeckl <p.stoeckl@ovido.at> 0.1-5
- some changes

* Thu Aug 29 2013 Rene Koch <r.koch@ovido.at> 0.1-4
- added SELinux support

* Thu Aug 29 2013 Rene Koch <r.koch@ovido.at> 0.1-3
- added requirement for perl-Crypt-SSLeay, perl-Time-HiRes and perl-DBD-MySQL

* Thu Aug 29 2013 Rene Koch <r.koch@ovido.at> 0.1-2
- added requirement for mod_fcgid and perl-FCGI

* Sun Aug 18 2013 Rene Koch <r.koch@ovido.at> 0.1-1
- Initial build.
