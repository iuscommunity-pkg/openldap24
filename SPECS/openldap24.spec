%define ldbm_backend berkeley
%define evolution_connector_prefix %{_libdir}/evolution-openldap
%define evolution_connector_includedir %{evolution_connector_prefix}/include
%define evolution_connector_libdir %{evolution_connector_prefix}/%{_lib}

%define name openldap24
%define real_name openldap
%define basever 2.4

Name: %{name}
Version: 2.4.32
Release: 2.ius%{?dist}
Summary: LDAP support libraries
Group: System Environment/Daemons
License: OpenLDAP
URL: http://www.openldap.org/
Source0: ftp://ftp.OpenLDAP.org/pub/OpenLDAP/openldap-release/openldap-%{version}.tgz
Source1: ldap.init
Source2: ldap.sysconfig
Source3: README.evolution
Source4: slapd.conf
Source5: slapd.portreserve
Source6: ldap.conf
Source54: libexec-create-certdb.sh
Source55: libexec-generate-server-cert.sh

# patches for the evolution library (see README.evolution)
Patch200: openldap-evolution-ntlm.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: cyrus-sasl-devel >= 2.1, nss-devel, krb5-devel, tcp_wrappers-devel, unixODBC-devel
BuildRequires: glibc-devel, libtool, libtool-ltdl-devel, groff, perl
# smbk5pwd overlay:
BuildRequires: openssl-devel
Requires: nss-tools

Obsoletes: compat-openldap < 2.4
# used by migrationtools:
Provides: ldif2ldbm

Provides: %{real_name} = %{version}-%{release}
Conflicts: %{real_name} < %{basever}

%description
OpenLDAP is an open source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. LDAP is a set of
protocols for accessing directory services (usually phone book style
information, but other information is possible) over the Internet,
similar to the way DNS (Domain Name System) information is propagated
over the Internet. The openldap package contains configuration files,
libraries, and documentation for OpenLDAP.

%package devel
Summary: LDAP development libraries and header files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: cyrus-sasl-devel >= 2.1
Provides: %{real_name}-devel = %{version}-%{release}
Conflicts: %{real_name}-devel < %{basever}
Provides: %{name}-evolution-devel = %{version}-%{release}
Provides: %{real_name}-evolution-devel = %{version}-%{release}

%description devel
The openldap-devel package includes the development libraries and
header files needed for compiling applications that use LDAP
(Lightweight Directory Access Protocol) internals. LDAP is a set of
protocols for enabling directory services over the Internet. Install
this package only if you plan to develop or will need to compile
customized LDAP clients.

%package servers
Summary: LDAP server
License: OpenLDAP
Requires: %{name} = %{version}-%{release}
Provides: %{real_name}-servers = %{version}-%{release}
Conflicts: %{real_name}-servers < %{basever}
Requires: openssl, portreserve
Requires(pre): shadow-utils, initscripts
Requires(post): chkconfig, /sbin/runuser, make, initscripts
Requires(preun): chkconfig, initscripts
BuildRequires: db4-devel >= 4.4, db4-devel < 4.9
Group: System Environment/Daemons

%description servers
OpenLDAP is an open-source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. LDAP is a set of
protocols for accessing directory services (usually phone book style
information, but other information is possible) over the Internet,
similar to the way DNS (Domain Name System) information is propagated
over the Internet. This package contains the slapd server and related files.

%package servers-sql
Summary: SQL support module for OpenLDAP server
Requires: %{name}-servers = %{version}-%{release}
Provides: %{real_name}-servers-sql = %{version}-%{release}
Conflicts: %{real_name}-servers-sql < %{basever}
Group: System Environment/Daemons

%description servers-sql
OpenLDAP is an open-source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. LDAP is a set of
protocols for accessing directory services (usually phone book style
information, but other information is possible) over the Internet,
similar to the way DNS (Domain Name System) information is propagated
over the Internet. This package contains a loadable module which the
slapd server can use to read data from an RDBMS.

%package clients
Summary: LDAP client utilities
Requires: %{name} = %{version}-%{release}
Provides: %{real_name}-clients = %{version}-%{release}
Conflicts: %{real_name}-clients < %{basever}
Group: Applications/Internet

%description clients
OpenLDAP is an open-source suite of LDAP (Lightweight Directory Access
Protocol) applications and development tools. LDAP is a set of
protocols for accessing directory services (usually phone book style
information, but other information is possible) over the Internet,
similar to the way DNS (Domain Name System) information is propagated
over the Internet. The openldap-clients package contains the client
programs needed for accessing and modifying OpenLDAP directories.

%prep
%setup -q -c -a 0 -n %{real_name}

# setup tree for openldap

pushd openldap-%{version}

for subdir in build-servers build-clients ; do
	mkdir $subdir
	ln -s ../configure $subdir
done

# build smbk5pwd with other overlays
ln -s ../../../contrib/slapd-modules/smbk5pwd/smbk5pwd.c servers/slapd/overlays
mv contrib/slapd-modules/smbk5pwd/README contrib/slapd-modules/smbk5pwd/README.smbk5pwd

popd

# setup tree for openldap with evolution-specific patches

if ! cp -al openldap-%{version} evo-openldap-%{version} ; then
	rm -fr evo-openldap-%{version}
	cp -a  openldap-%{version} evo-openldap-%{version}
fi
pushd evo-openldap-%{version}
%patch200 -p1 -b .evolution-ntlm
popd

%build

libtool='%{_bindir}/libtool'
export tagname=CC

%ifarch ia64
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -O0"
%endif

export CPPFLAGS="-I%_includedir/nss3 -I%_includedir/nspr4"
export CFLAGS="$RPM_OPT_FLAGS $CPPFLAGS -fno-strict-aliasing -fPIC -D_REENTRANT -DLDAP_CONNECTIONLESS -D_GNU_SOURCE -DHAVE_TLS -DHAVE_MOZNSS -DSLAPD_LMHASH"
export NSS_LIBS="-lssl3 -lsmime3 -lnss3 -lnssutil3 -lplds4 -lplc4 -lnspr4"
export LIBS=""
export LDFLAGS="$LDFLAGS -Wl,-z,relro"

build() {

%configure \
    --with-threads=posix \
    \
    --enable-local \
	--enable-rlookups \
    \
    --with-tls=no \
    --with-cyrus-sasl \
    \
    --enable-wrappers \
    \
    --enable-passwd \
    \
    --enable-cleartext \
    --enable-crypt \
    --enable-spasswd \
    --disable-lmpasswd \
    --enable-modules \
    --disable-sql \
    \
    --libexecdir=%{_libdir} \
    $@

# allow #include <nss/file.h> and <nspr/file.h>
pushd include
if [ ! -d nss ] ; then
    ln -s %{_includedir}/nss3 nss
fi
if [ ! -d nspr ] ; then
    ln -s %{_includedir}/nspr4 nspr
fi
popd

make %{_smp_mflags} LIBTOOL="$libtool"

}

# Kerberos support:
# - enabled in server (mainly for password checking)
# - disabled in clients (not needed, to avoid stray dependencies)

# build servers
export LIBS="$NSS_LIBS -lpthread"
pushd openldap-%{version}/build-servers
build \
    --enable-plugins \
    --enable-slapd \
    --enable-multimaster \
    --enable-bdb \
    --enable-hdb \
    --enable-ldap \
    --enable-ldbm \
    --with-ldbm-api=%{ldbm_backend} \
    --enable-meta \
    --enable-monitor \
    --enable-null \
    --enable-shell \
    --enable-sql=mod \
    --disable-ndb \
    --enable-passwd \
    --enable-sock \
    --disable-perl \
    --enable-relay \
    --disable-shared \
    --disable-dynamic \
    --with-kerberos=k5only \
    --enable-overlays=mod
popd

# build clients
export LIBS="$NSS_LIBS"
pushd openldap-%{version}/build-clients
build \
    --disable-slapd \
    --enable-shared \
    --enable-dynamic \
    --without-kerberos \
    --with-pic
popd

# build evolution-specific clients
# (specific patch, different installation directory, no shared libraries)
pushd evo-openldap-%{version}
build \
    --disable-slapd \
    --disable-shared \
    --disable-dynamic \
    --enable-static \
    --without-kerberos \
    --with-pic \
    --includedir=%{evolution_connector_includedir} \
    --libdir=%{evolution_connector_libdir}
popd

%install
rm -rf %{buildroot}
libtool='%{_bindir}/libtool'
export tagname=CC

mkdir -p %{buildroot}/%{_libdir}/

# install servers
pushd openldap-%{version}/build-servers
make install DESTDIR=%{buildroot} \
	libdir=%{_libdir} \
	LIBTOOL="$libtool" \
	STRIP=""
popd

# install evolution-specific clients (conflicting files will be overwriten by generic version)
pushd evo-openldap-%{version}
make install DESTDIR=%{buildroot} \
    includedir=%{evolution_connector_includedir} \
    libdir=%{evolution_connector_libdir} \
    LIBTOOL="$libtool" \
    STRIP=""
install -m 644 %SOURCE3 \
    %{buildroot}/%{evolution_connector_prefix}/
popd

# install clients
pushd openldap-%{version}/build-clients
make install DESTDIR=%{buildroot} \
	libdir=%{_libdir} \
	LIBTOOL="$libtool" \
	STRIP=""
popd

# setup directories for TLS certificates
mkdir -p %{buildroot}%{_sysconfdir}/openldap/certs

# setup data and runtime directories
mkdir -p %{buildroot}/var/lib/ldap
mkdir -p %{buildroot}/var/run/openldap

# remove build root from config files and manual pages
perl -pi -e "s|%{buildroot}||g" %{buildroot}/%{_sysconfdir}/openldap/*.conf
perl -pi -e "s|%{buildroot}||g" %{buildroot}%{_mandir}/*/*.*

# we don't need the default files -- RPM handles changes
rm -f %{buildroot}/%{_sysconfdir}/openldap/*.default
rm -f %{buildroot}/%{_sysconfdir}/openldap/schema/*.default

# install an init script for the servers
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
install -m 755 %SOURCE1 %{buildroot}%{_sysconfdir}/rc.d/init.d/slapd

# install syconfig/ldap
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %SOURCE2 %{buildroot}%{_sysconfdir}/sysconfig/ldap

# install portreserve config
mkdir -p %{buildroot}%{_sysconfdir}/portreserve
install -m 644 %SOURCE5 %{buildroot}%{_sysconfdir}/portreserve/slapd

# install default ldap.conf (customized)
rm -f %{buildroot}%{_sysconfdir}/openldap/ldap.conf
install -m 0644 %SOURCE6 %{buildroot}%{_sysconfdir}/openldap/ldap.conf

# setup maintainance scripts
mkdir -p %{buildroot}%{_libexecdir}
install -m 0755 -d %{buildroot}%{_libexecdir}/openldap
install -m 0755 %SOURCE54 %{buildroot}%{_libexecdir}/openldap/create-certdb.sh
install -m 0755 %SOURCE55 %{buildroot}%{_libexecdir}/openldap/generate-server-cert.sh

# move slapd out of _libdir
mv %{buildroot}/%{_libdir}/slapd %{buildroot}/%{_sbindir}/

# setup tools as symlinks to slapd
rm -f %{buildroot}/%{_sbindir}/slap{acl,add,auth,cat,dn,index,passwd,test,schema}
rm -f %{buildroot}/%{_libdir}/slap{acl,add,auth,cat,dn,index,passwd,test,schema}
for X in acl add auth cat dn index passwd test schema; do ln -s slapd %{buildroot}/%{_sbindir}/slap$X ; done

# tweak permissions on the libraries to make sure they're correct
chmod 755 %{buildroot}/%{_libdir}/lib*.so*
chmod 644 %{buildroot}/%{_libdir}/lib*.*a

# slapd.conf(5) is obsoleted since 2.3, see slapd-config(5)
# new configuration will be generated in %post
mkdir -p %{buildroot}/%{_datadir}/openldap-servers
mkdir %{buildroot}/%{_sysconfdir}/openldap/slapd.d
rm -f %{buildroot}/%{_sysconfdir}/openldap/slapd.conf
install -m 644 %SOURCE4 %{buildroot}/%{_datadir}/openldap-servers/slapd.conf.obsolete

# move doc files out of _sysconfdir
mv %{buildroot}%{_sysconfdir}/openldap/schema/README README.schema
mv %{buildroot}%{_sysconfdir}/openldap/DB_CONFIG.example %{buildroot}/%{_datadir}/openldap-servers/DB_CONFIG.example
chmod 0644 openldap-%{version}/servers/slapd/back-sql/rdbms_depend/timesten/*.sh
chmod 0644 %{buildroot}/%{_datadir}/openldap-servers/DB_CONFIG.example

# move all libraries from /usr/lib to /lib for disk-less booting
# devel symlinks will be left in the original location
mkdir -p %{buildroot}/%{_lib}
pushd %{buildroot}/%{_libdir}
# versioned libraries
mv {libldap,libldap_r,liblber}-*.so* %{buildroot}/%{_lib}
# update devel symlinks
for library in {libldap,libldap_r,liblber}.so; do
	[ -h $library ] || exit 1
	ln -sf /%{_lib}/$(readlink $library) $library
done
popd

# remove files which we don't want packaged
rm -f %{buildroot}/%{_libdir}/*.la
rm -f %{buildroot}/%{_libdir}/*.a
rm -f %{buildroot}/%{evolution_connector_libdir}/*.la
rm -f %{buildroot}/%{evolution_connector_libdir}/*.so*
rm -f %{buildroot}/%{_libdir}/openldap/*.a
rm -f %{buildroot}/%{_libdir}/openldap/*.so

rm -f %{buildroot}%{_localstatedir}/openldap-data/DB_CONFIG.example
rmdir %{buildroot}%{_localstatedir}/openldap-data

%clean 
rm -rf %{buildroot}

%post
/sbin/ldconfig
# create certificate database
%{_libexecdir}/openldap/create-certdb.sh >&/dev/null || :

%postun -p /sbin/ldconfig

%pre servers

# create ldap user and group
getent group ldap >/dev/null || groupadd -r -g 55 ldap
if ! getent passwd ldap >/dev/null; then
	useradd -r -g ldap -u 55 -d %{_sharedstatedir}/ldap -s /sbin/nologin -c "LDAP User" ldap
	# setup ownership of database files
	if [ -d /var/lib/ldap ] ; then
		for dbfile in /var/lib/ldap/* ; do
			if [ -f $dbfile ] ; then
				chown ldap:ldap $dbfile
			fi
		done
	fi
fi

# upgrade
if [ $1 -eq 2 ]; then
	# safe way to migrate the database if version number changed
	# http://www.openldap.org/doc/admin24/maintenance.html

	old_version=$(rpm -q --qf=%%{version} openldap-servers)
	new_version=%{version}

	if [ "$old_version" != "$new_version" ]; then
		pushd %{_sharedstatedir}/ldap &>/dev/null

		# stop the service
		if /sbin/service slapd status &>/dev/null; then
			touch need_start
			/sbin/service slapd stop
		else
			rm -f need_start
		fi

		if ls *.bdb &>/dev/null; then
			# symlink to last backup
			rm -f upgrade.ldif

			# backup location
			backupdir=backup.$(date +%%s)
			backupfile=${backupdir}/backup.ldif
			backupcmd="cp -a"

			mkdir -p ${backupdir}

			# database recovery tool
			# (this is necessary to handle upgrade from old openldap, which had embedded db4)
			if [ -f /usr/sbin/slapd_db_recover ]; then
				db_recover=/usr/sbin/slapd_db_recover
			else
				db_recover=/usr/bin/db_recover
			fi

			# make sure the database is consistent
			runuser -m -s $db_recover -- "ldap" -h %{_sharedstatedir}/ldap &>/dev/null

			# export the database if possible
			if [ $? -eq 0 ]; then
				if [ -f %{_sysconfdir}/openldap/slapd.conf ]; then
					slapcat -f %{_sysconfdir}/openldap/slapd.conf -l $backupfile &>/dev/null
				else
					slapcat -F %{_sysconfdir}/openldap/slapd.d -l $backupfile &>/dev/null
				fi

				if [ $? -eq 0 ]; then
					chmod 0400 $backupfile
					ln -sf $backupfile upgrade.ldif
					backupcmd=mv
				fi
			fi

			# move or copy to backup directory
			find -maxdepth 1 -type f \( -name alock -o -name "*.bdb" -o -name "__db.*" -o -name "log.*" \) \
				| xargs -I '{}' $backupcmd '{}' $backupdir
			cp -af DB_CONFIG $backupdir &>/dev/null

			# fix permissions
			chown -R ldap: $backupdir
			chmod -R a-w $backupdir
		fi

		popd &>/dev/null
	fi
fi

exit 0

%post servers

/sbin/ldconfig
/sbin/chkconfig --add slapd

# generate sample TLS certificates for server (will not replace)
%{_libexecdir}/openldap/generate-server-cert.sh -o &>/dev/null || :

# generate configuration in slapd.d
if ! ls -d %{_sysconfdir}/openldap/slapd.d/* &>/dev/null; then

	# fresh installation
	[ ! -f %{_sysconfdir}/openldap/slapd.conf ]
	fresh_install=$?

	[ $fresh_install -eq 0 ] && \
		cp %{_datadir}/openldap-servers/slapd.conf.obsolete %{_sysconfdir}/openldap/slapd.conf

	# convert from old style config slapd.conf
	mv %{_sysconfdir}/openldap/slapd.conf %{_sysconfdir}/openldap/slapd.conf.bak
	mkdir -p %{_sysconfdir}/openldap/slapd.d/
	slaptest -f %{_sysconfdir}/openldap/slapd.conf.bak -F %{_sysconfdir}/openldap/slapd.d &>/dev/null
	chown -R ldap:ldap %{_sysconfdir}/openldap/slapd.d
	chmod -R 000 %{_sysconfdir}/openldap/slapd.d
	chmod -R u+rwX %{_sysconfdir}/openldap/slapd.d
	rm -f %{_sysconfdir}/openldap/slapd.conf
	rm -f %{_sharedstatedir}/ldap/__db* %{_sharedstatedir}/ldap/alock

	[ $fresh_install -eq 0 ] && rm -f %{_sysconfdir}/openldap/slapd.conf.bak
fi

# finish database migration (see %pre)
if [ -f %{_sharedstatedir}/ldap/upgrade.ldif ]; then
	runuser -m -s /usr/sbin/slapadd -- ldap -q -l %{_sharedstatedir}/ldap/upgrade.ldif &>/dev/null
	rm -f %{_sharedstatedir}/ldap/upgrade.ldif
fi

# restart after upgrade
if [ $1 -ge 1 ]; then
	if [ -f %{_sharedstatedir}/ldap/need_start ]; then
		/sbin/service slapd start
		rm -f %{_sharedstatedir}/ldap/need_start
	else
		/sbin/service slapd condrestart
	fi
fi

exit 0

%preun servers
if [ $1 -eq 0 ] ; then
	/sbin/service slapd stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del slapd

	# openldap-servers are being removed from system
	# do not touch the database!
fi

%postun servers
/sbin/ldconfig

%post devel -p /sbin/ldconfig

%postun devel -p /sbin/ldconfig

%triggerin servers -- db4

# db4 upgrade (see %triggerun)
if [ $2 -eq 2 ]; then
	pushd %{_sharedstatedir}/ldap &>/dev/null

	# we are interested in minor version changes (both versions of db4 are installed at this moment)
	if [ "$(rpm -q --qf="%%{version}\n" db4 | sed 's/\.[0-9]*$//' | sort -u | wc -l)" != "1" ]; then
		# stop the service
		if /sbin/service slapd status &>/dev/null; then
			touch need_start
			/sbin/service slapd stop
		fi

		# ensure the database is consistent
		runuser -m -s /usr/bin/db_recover -- "ldap" -h %{_sharedstatedir}/ldap &>/dev/null

		# upgrade will be performed after removing old db4
		touch upgrade_db4
	else
		rm -f upgrade_db4
	fi

	popd &>/dev/null
fi

exit 0

%triggerun servers -- db4

# db4 upgrade (see %triggerin)
if [ -f %{_sharedstatedir}/ldap/upgrade_db4 ]; then
	pushd %{_sharedstatedir}/ldap &>/dev/null

	# perform the upgrade
	if ls *.bdb &>/dev/null; then
		runuser -m -s /usr/bin/db_upgrade -- "ldap" -h %{_sharedstatedir}/ldap %{_sharedstatedir}/ldap/*.bdb
		runuser -m -s /usr/bin/db_checkpoint -- "ldap" -h %{_sharedstatedir}/ldap -1
	fi

	# start the service
	if [ -f need_start ]; then
		/sbin/service slapd start
		rm -f need_start
	fi

	rm -f upgrade_db4
	popd &>/dev/null
fi

exit 0

%files
%defattr(-,root,root)
%doc openldap-%{version}/ANNOUNCEMENT
%doc openldap-%{version}/CHANGES
%doc openldap-%{version}/COPYRIGHT
%doc openldap-%{version}/LICENSE
%doc openldap-%{version}/README
%attr(0755,root,root) %dir %{_sysconfdir}/openldap
%attr(0755,root,root) %dir %{_sysconfdir}/openldap/certs
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/openldap/ldap*.conf
%attr(0755,root,root) /%{_lib}/libl*-2.4*.so.*
%attr(0644,root,root) %{_mandir}/man5/ldif.5*
%attr(0644,root,root) %{_mandir}/man5/ldap.conf.5*
%{_libexecdir}/openldap/create-certdb.sh

%files servers
%defattr(-,root,root)
%doc openldap-%{version}/contrib/slapd-modules/smbk5pwd/README.smbk5pwd
%doc openldap-%{version}/doc/guide/admin/*.html
%doc openldap-%{version}/doc/guide/admin/*.png
%doc README.schema
%attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/slapd
%attr(0750,ldap,ldap) %dir %config(noreplace) %{_sysconfdir}/openldap/slapd.ldif
%attr(0750,ldap,ldap) %dir %config(noreplace) %{_sysconfdir}/openldap/slapd.d
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/ldap
%attr(0755,root,root) %dir %config(noreplace) %{_sysconfdir}/openldap/schema
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/openldap/schema/*.schema*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/openldap/schema/*.ldif
%attr(0644,root,root) %{_sysconfdir}/portreserve/slapd
%attr(0755,root,root) %{_sbindir}/sl*
%attr(0644,root,root) %{_mandir}/man8/*
%attr(0644,root,root) %{_mandir}/man5/slapd*.5*
%attr(0644,root,root) %{_mandir}/man5/slapo-*.5*
%attr(0700,ldap,ldap) %dir /var/lib/ldap
%attr(0755,ldap,ldap) %dir /var/run/openldap
%attr(0755,root,root) %dir %{_libdir}/openldap
%attr(0755,root,root) %{_libdir}/openldap/[^b]*
%attr(0755,root,root) %dir %{_datadir}/openldap-servers
%attr(0644,root,root) %{_datadir}/openldap-servers/*
# obsolete configuration
%attr(0640,ldap,ldap) %ghost %config(noreplace,missingok) %{_sysconfdir}/openldap/slapd.conf
%attr(0640,ldap,ldap) %ghost %config(noreplace,missingok) %{_sysconfdir}/openldap/slapd.conf.bak
%{_libexecdir}/openldap/generate-server-cert.sh

%files servers-sql
%defattr(-,root,root)
%doc openldap-%{version}/servers/slapd/back-sql/docs/*
%doc openldap-%{version}/servers/slapd/back-sql/rdbms_depend
%attr(0755,root,root) %{_libdir}/openldap/back_sql*.so.*
%attr(0755,root,root) %{_libdir}/openldap/back_sql.la

%files clients
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) %{_mandir}/man1/*

%files devel
%defattr(-,root,root)
%doc openldap-%{version}/doc/drafts openldap-%{version}/doc/rfc
%attr(0755,root,root) %{_libdir}/libl*.so
%attr(0644,root,root) %{_includedir}/*
%attr(0644,root,root) %{_mandir}/man3/*
%attr(0755,root,root) %dir %{evolution_connector_prefix}
%attr(0644,root,root)      %{evolution_connector_prefix}/README*
%attr(0755,root,root) %dir %{evolution_connector_includedir}
%attr(0644,root,root)      %{evolution_connector_includedir}/*.h
%attr(0755,root,root) %dir %{evolution_connector_libdir}
%attr(0644,root,root)      %{evolution_connector_libdir}/*.a

%changelog
* Wed Dec 05 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.4.32-2.ius
- Adding in needed Conflicts

* Wed Aug 15 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.4.32-1.ius
- Porting to IUS from Enterprise Linux 6
- Latest sources

* Mon May 07 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-26
- fix: MozNSS CA cert dir does not work together with PEM CA cert file (#818844)
- fix: memory leak: def_urlpre is not freed (#816168)
- fix update: Default SSL certificate bundle is not found by openldap library (#742023)

* Wed May 02 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-25
- fix update: Default SSL certificate bundle is not found by openldap library (#742023)

* Mon Apr 30 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-24
- fix update: Default SSL certificate bundle is not found by openldap library (#742023)
- fix: memberof overlay on the frontend database causes server segfault (#730745)

* Fri Apr 20 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-23
- security fix: CVE-2012-1164: assertion failure by processing search queries
  requesting only attributes for particular entry (#813162)

* Tue Apr 10 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-22
- fix: libraries leak memory when following referrals (#807363)

* Thu Mar 01 2012 Jan Vcelak <jvcelak@redhat.com> 2.4.23-21
- fix: ldapsearch crashes with invalid parameters (#743781)
- fix: replication (syncrepl) with TLS causes segfault (#783445)
- fix: openldap server in MirrorMode sometimes fails to resync via syncrepl (#784211)
- use portreserve to reserve LDAPS port (636/tcp+udp) (#790687)
- fix: missing options in manual pages of client tools (#745470)
- fix: SASL_NOCANON option missing in ldap.conf manual page (#732916)
- fix: slapd segfaults when certificate key cannot be loaded (#796808)
- Jan Synáček <jsynacek@redhat.com>
  + fix: overlay constraint with count option work bad with modify operation (#742163)
  + fix: Default SSL certificate bundle is not found by openldap library (#742023)
  + fix: Duplicate close() calls in OpenLDAP (#784203)

* Tue Oct 04 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-20
- new feature update: honor priority/weight with ldap_domain2hostlist (#730311)
- fix regression: openldap built without tcp_wrappers (#742592)

* Tue Sep 13 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-19
- fix: SSL_ForceHandshake function is not thread safe (#709407)

* Fri Aug 26 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-18
- fix: overlay refint option refint_nothing doesn't function correctly (#725479)
- fix: Unwanted slash printed when installing openldap-servers (#732001)
- manpage fix: TLS options in documentation are not valid for MozNSS (#684810)
- fix: NSS_Init* functions are not thread safe (#731168)
- manpage fix: errors in manual page slapo-unique (#723521) 
- new feature: honor priority/weight with ldap_domain2hostlist (#730311)

* Mon Aug 15 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-17
- fix: strict aliasing warnings during package build (#723487)
- add partial RELRO support for libraries (#723999)
- fix: incorrect behavior of allow/try options of VerifyCert and TLS_REQCERT (#729095)
- fix: memleak - free the return of tlsm_find_and_verify_cert_key (#729087)
- fix: TLS_REQCERT=never ignored when the certificate is expired (#722959)
- fix: matching wildcard hostnames in certificate Subject field does not work (#726984)
- fix: OpenLDAP server segfaults when using back-sql (#727533)
- fix: conversion of constraint overlay settings to cn=config is incorrect (#722923)
- fix: DDS overlay tolerance parametr doesn't function and breakes default TTL (#723514)

* Mon Jul 18 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-16
- fix: memleak in tlsm_auth_cert_handler (#717738)
- fix: segmentation fault of client tool when LDIF input file is not terminated
  by a new line character (#698921)
- fix: segmentation fault of client tool when input line in LDIF file
  is splitted but indented incorrectly (#701227)
- fix: server scriptlets require initscripts package (#712358)
- enable ldapi:/// interface by default
- set cn=config management ACLs for root user, SASL external schema (#712494)
- fix: ldapsearch fails if no CA certificate is available (#713525)

* Wed Apr 13 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-15
- fix: rpm -V fail when upgrading with openldap-devel installed (#693716)
  (remove devel *.so symlinks from /lib and leave them in /usr/lib)

* Fri Mar 18 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-14
- fix update: openldap startup script ignores ulimit settings (#679356)
- fix update: openldap-servers upgrade hangs or do not upgrade the database (#685119)

* Mon Mar 14 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-13
- fix update: openldap can't use TLS after a fork() (#671553)
- fix: possible NULL pointer dereferences in NSS non-blocking patch (#684035)
- fix: move libldif to /lib for consistency (#548475)
- fix: openldap-servers upgrade hangs or do not upgrade the database (#685119)

* Tue Mar 01 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-12
- fix: security - DoS when submitting special MODRDN request (#680975)

* Mon Feb 28 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-11
- fix: CVE-2011-1024 ppolicy forwarded bind failure messages cause success
- fix: CVE-2011-1025 rootpw is not verified for ndb backend
- fix: openldap startup script ignores ulimit settings (#679356)
- fix: add symlinks into /usr/lib*/ (#680139)

* Mon Feb 21 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-10
- fix: add symlinks for libraries moved in 2.4.23-5 to allow building
  packages which require these libraries in the old location (#678105)

* Wed Feb 02 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-9
- fix update: openldap can't use TLS after a fork() (#671553)

* Tue Jan 25 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-8
- fix: openldap can't use TLS after a fork() (#671553)

* Thu Jan 20 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-7
- fix: some server certificates refused with inadequate type error (#669846)
- fix: default encryption strength dropped in switch to using NSS (#669845)

* Thu Jan 13 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-6
- fix update: openldap-devel symlinks to libraries were not moved correctly (#548475)

* Thu Jan 13 2011 Jan Vcelak <jvcelak@redhat.com> 2.4.23-5
- initscript: slaptest with '-u' to skip database opening (#613966)
- removed slurpd options from sysconfig/ldap
- fix: verification of self issued certificates (#667795)
- fix: move libraries from /usr/lib to /lib (#548475)

* Sat Dec 04 2010 Jan Vcelak <jvcelak@redhat.com> 2.4.23-4
- rebase to 2.4.23 (Fedora 14) (#644077)
- uses Mozilla NSS instead of OpenSSL for TLS/SSL
- added LDIF (ldif.h) to the public API
- removed embeded Berkeley DB
- removed autofs schema (use up-to-date version from autofs package instead)
- removed compat-openldap subpackage (use separate package instead)
- fixes: ldapsearch -Z hangs server if starttls fails (#652823)
- fixes: improve SSL/TLS log messages (#652819)
- fixes: crash when TLS_CACERTDIR contains a subdirectory (#652817)
- fixes: TLS_CACERTDIR takes precedence over TLS_CACERT (#652816)
- fixes: openldap should ignore files not in the openssl c_hash format in cacertdir (#652814)
- fixes: slapd init script gets stuck in an infinite loop (#644399)
- fixes: Remove lastmod.la from default slapd.conf.bak (#630637)
- fixes: Mozilla NSS - delay token auth until needed (#616558)
- fixes: Mozilla NSS - support use of self signed CA certs as server certs (#616554)

* Fri Jun 25 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-15
- fixed regression caused by tls accept patch (#608112)

* Tue Jun 22 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-14
- fixed segfault issue in modrdn (#606369)

* Fri Jun 18 2010 Jan Vcelak <jvcelak@redhat.com> 2.4.19-13
- implementation of ulimit settings for slapd (#602458)

* Wed May 26 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-12
- updated man pages - only slaptest can convert configuration schema
  (#584787)
- openldap compiled with -fno-strict-aliasing (#596193)

* Thu May 06 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-11
- added compat package

* Tue Apr 27 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-10
- updated overlay list in config file (#586143)
- config dir slapd.d added to package payload (#585276)
- init script now creates only symlink, not harldink, in /var/run (#584870)

* Mon Apr 19 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-9
- fixed broken link /usr/sbin/slapschema (#583568)
- removed some static libraries from openldap-devel (#583575)

* Fri Apr 16 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-8
- updated spec file - clean files generated by configuration conversion
  (#582327)

* Mon Mar 22 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-7
- updated usage line in init script
- changed return code when calling init script with bad arguments

* Mon Mar 22 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-6
- fixed segfault when using hdb backend (#575403)

* Fri Mar 19 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-5
- minor corrections of init script (fedora bugs #571235, #570057, #573804)

* Wed Feb 10 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-4
- removed syncprov.la from config file (#563472)

* Wed Feb 03 2010 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-3
- updated post scriptlet (#561352)

* Mon Nov 23 2009 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-2
- minor changes in init script

* Wed Nov 18 2009 Jan Zeleny <jzeleny@redhat.com> - 2.4.19-1
- fixed tls connection accepting when TLSVerifyClient = allow
- /etc/openldap/ldap.conf removed from files owned by openldap-servers
- minor changes in spec file to supress warnings
- some changes in init script, so it would be possible to use it when
  using old configuration style
- rebased openldap to 2.4.19
- rebased bdb to 4.8.24

* Wed Oct 07 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.18-5
- updated smbk5pwd patch to be linked with libldap (#526500)

* Wed Sep 30 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.18-4
- buffer overflow patch from upstream
- added /etc/openldap/slapd.d and /etc/openldap/slapd.conf.bak
  to files owned by openldap-servers

* Thu Sep 24 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.18-3
- cleanup of previous patch fixing buffer overflow

* Tue Sep 22 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.18-2
- changed configuration approach. Instead od slapd.conf slapd
  is using slapd.d directory now
- fix of some issues caused by renaming of init script
- fix of buffer overflow issue in ldif.c pointed out by new glibc

* Fri Sep 18 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.18-1
- rebase of openldap to 2.4.18

* Wed Sep 16 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.16-7
- updated documentation (hashing the cacert dir)

* Wed Sep 16 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.16-6
- updated init script to be LSB-compliant (#523434)
- init script renamed to slapd

* Thu Aug 27 2009 Tomas Mraz <tmraz@redhat.com> - 2.4.16-5
- rebuilt with new openssl

* Tue Aug 25 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.16-4
- updated %pre script to correctly install openldap group

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 01 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.16-1
- rebase of openldap to 2.4.16
- fixed minor issue in spec file (output looking interactive
  when installing servers)

* Tue Jun 09 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.15-4
- added $SLAPD_URLS variable to init script (#504504)

* Thu Apr 09 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.15-3
- extended previous patch (#481310) to remove options cfMP
  from some client tools
- correction of patch setugid (#494330)

* Thu Mar 26 2009 Jan Zeleny <jzeleny@redhat.com> 2.4.15-2
- removed -f option from some client tools (#481310)

* Wed Feb 25 2009 Jan Safranek <jsafranek@redhat.com> 2.4.15-1
- new upstream release

* Tue Feb 17 2009 Jan Safranek <jsafranek@redhat.com> 2.4.14-1
- new upstream release
- upgraded to db-4.7.25

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> 2.4.12-3
- rebuild with new openssl

* Mon Dec 15 2008 Caolán McNamara <caolanm@redhat.com> 2.4.12-2
- rebuild for libltdl, i.e. copy config.sub|guess from new location

* Wed Oct 15 2008 Jan Safranek <jsafranek@redhat.com> 2.4.12-1
- new upstream release

* Mon Oct 13 2008 Jan Safranek <jsafranek@redhat.com> 2.4.11-3
- add SLAPD_SHUTDOWN_TIMEOUT to /etc/sysconfig/ldap, allowing admins
  to set non-default slapd shutdown timeout
- add checkpoint to default slapd.conf file (#458679)

* Mon Sep  1 2008 Jan Safranek <jsafranek@redhat.com> 2.4.11-2
- provide ldif2ldbm functionality for migrationtools
- rediff all patches to get rid of patch fuzz

* Mon Jul 21 2008 Jan Safranek <jsafranek@redhat.com> 2.4.11-1
- new upstream release
- apply official bdb-4.6.21 patches

* Wed Jul  2 2008 Jan Safranek <jsafranek@redhat.com> 2.4.10-2
- fix CVE-2008-2952 (#453728)

* Thu Jun 12 2008 Jan Safranek <jsafranek@redhat.com> 2.4.10-1
- new upstream release

* Wed May 28 2008 Jan Safranek <jsafranek@redhat.com> 2.4.9-5
- use /sbin/nologin as shell of ldap user (#447919)

* Tue May 13 2008 Jan Safranek <jsafranek@redhat.com> 2.4.9-4
- new upstream release
- removed unnecessary MigrationTools patches

* Thu Apr 10 2008 Jan Safranek <jsafranek@redhat.com> 2.4.8-4
- bdb upgraded to 4.6.21
- reworked upgrade logic again to run db_upgrade when bdb version
  changes

* Wed Mar  5 2008 Jan Safranek <jsafranek@redhat.com> 2.4.8-3
- reworked the upgrade logic, slapcat/slapadd of the whole database
  is needed only if minor version changes (2.3.x -> 2.4.y)
- do not try to save database in LDIF format, if openldap-servers package 
  is  being removed (it's up to the admin to do so manually)

* Thu Feb 28 2008 Jan Safranek <jsafranek@redhat.com> 2.4.8-2
- migration tools carved out to standalone package "migrationtools"
  (#236697)

* Fri Feb 22 2008 Jan Safranek <jsafranek@redhat.com> 2.4.8-1
- new upstream release

* Fri Feb  8 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-7
- fix CVE-2008-0658 (#432014)

* Mon Jan 28 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-6
- init script fixes

* Mon Jan 28 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-5
- init script made LSB-compliant (#247012)

* Fri Jan 25 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-4
- fixed rpmlint warnings and errors
  - /etc/openldap/schema/README moved to /usr/share/doc/openldap

* Tue Jan 22 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-3
- obsoleting compat-openldap properly again :)

* Tue Jan 22 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-2
- obsoleting compat-openldap properly (#429591)

* Mon Jan 14 2008 Jan Safranek <jsafranek@redhat.com> 2.4.7-1
- new upstream version (openldap-2.4.7)
