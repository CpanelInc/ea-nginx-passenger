Name:           ea-nginx-passenger
Version:        6.1.0
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4552 for more details
%define release_prefix 4
Release:        %{release_prefix}%{?dist}.cpanel
Summary:        Provides passenger module for ea-nginx
License:        MIT
URL:            https://www.phusionpassenger.com
Group:          System Environment/Libraries
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:  ea-nginx-ngxdev
BuildRequires:  ea-passenger-src

%if 0%{?rhel} == 7
BuildRequires: devtoolset-8 devtoolset-8-gcc devtoolset-8-gcc-c++ kernel-devel
%endif

%if 0%{?rhel} > 8
BuildRequires: libcurl
BuildRequires: libcurl-devel
BuildRequires: brotli
BuildRequires: brotli-devel
%else
BuildRequires: libcurl
BuildRequires: libcurl-devel
BuildRequires: ea-brotli
BuildRequires: ea-brotli-devel
BuildRequires: brotli
BuildRequires: brotli-devel
Requires: ea-brotli
Requires: brotli
Requires: libcurl
%endif

%define ruby_version ea-ruby27

%if 0%{?rhel} >= 9
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: rubygem-rake
%else
BuildRequires: ea-apache24-devel
BuildRequires: %{ruby_version}-rubygem-rake >= 0.8.1
BuildRequires: %{ruby_version}-rubygem-passenger
BuildRequires: %{ruby_version}-ruby-devel
BuildRequires: %{ruby_version}
Requires:      %{ruby_version}
%endif

Requires: apache24-passenger

Requires: ea-nginx >= 1:1.25.1-3
Requires: ea-passenger-runtime

Source1:  ea-nginx-passenger-module.conf
Source2:  update_ruby_shebang.pl
Source3:  ngx_http_passenger_module.conf.tt

%description
This module provides Phusion Passenger app support for ea-nginx

%prep
set -x
cp -rf /opt/cpanel/ea-passenger-src/passenger-*/ .
cp %{SOURCE2} .

%build
set -x
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-8/enable
%endif

%if 0%{?rhel} <= 8
export PATH=/opt/cpanel/ea-ruby27/root/usr/bin:$PATH
export GEM_PATH=%{gem_dir}:${GEM_PATH:+${GEM_PATH}}${GEM_PATH:-`scl enable ea-ruby27 -- ruby -e "print Gem.path.join(':')"`}
gem env
%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags)) -fPIC -I/opt/cpanel/ea-brotli/include -I/opt/cpanel/%{ruby_version}/root/usr/include -I/opt/cpanel/ea-passenger-src/passenger-release-%{version}/src/nginx_module
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie -ldl -Wl,-rpath=/opt/cpanel/ea-brotli/lib

%if 0%{?rhel} == 8
EXTRA_CXX_LDFLAGS="-L/opt/cpanel/ea-ruby27/root/usr/lib64 -L/usr/lib64 -lcurl -lssl -lcrypto -lgssapi_krb5 -lkrb5 -lk5crypto -lkrb5support -lssl -lcrypto -lssl -lcrypto -Wl,-rpath=%{_libdir},--enable-new-dtags -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto -lssl -lcrypto "; export EXTRA_CXX_LDFLAGS;
export EXTRA_CXXFLAGS="-I/opt/cpanel/ea-ruby27/root/usr/include -I/usr/include"
%endif

cd passenger-release-%{version}/
perl %{SOURCE2}
cd ..
%endif

. /opt/cpanel/ea-nginx-ngxdev/set_NGINX_CONFIGURE_array.sh
./auto/configure "${NGINX_CONFIGURE[@]}" \
    --add-dynamic-module=../passenger-release-%{version}/src/nginx_module \
%if 0%{?rhel} <= 8
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
%endif

make

popd

%install
set -x

install -D %{SOURCE1} %{buildroot}/etc/nginx/conf.d/modules/ea-nginx-passenger-module.conf
install -D %{SOURCE3} %{buildroot}/etc/nginx/ea-nginx/ngx_http_passenger_module.conf.tt
install -D ./nginx-build/objs/ngx_http_passenger_module.so %{buildroot}%{_libdir}/nginx/modules/ngx_http_passenger_module.so

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
/etc/nginx/conf.d/modules/ea-nginx-passenger-module.conf
/etc/nginx/ea-nginx/ngx_http_passenger_module.conf.tt
%attr(0755,root,root) %{_libdir}/nginx/modules/ngx_http_passenger_module.so

%changelog
* Tue Dec 09 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.1.0-4
- EA-13286: Build against ea-nginx version v1.29.4

* Tue Oct 28 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.27-3
- EA-13235: Build against ea-nginx version v1.29.3
- ea-passenger-src was updated from v6.0.27 to v6.1.0

* Wed Aug 13 2025 Dan Muey <daniel.muey@webpros.com> - 6.0.27-2
- EA-13069: Build against ea-nginx version v1.29.1

* Fri Apr 04 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.27-1
- EA-12801: ea-passenger-src was updated from v6.0.26 to v6.0.27

* Wed Feb 19 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.26-1
- EA-12725: ea-passenger-src was updated from v6.0.25 to v6.0.26

* Wed Feb 19 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.25-1
- EA-12724: ea-passenger-src was updated from v6.0.24 to v6.0.25

* Tue Feb 11 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.24-2
- EA-12703: Build against ea-nginx version v1.26.3

* Mon Feb 10 2025 Cory McIntire <cory.mcintire@webpros.com> - 6.0.24-1
- EA-12681: ea-passenger-src was updated from v6.0.23 to v6.0.24
- EA-12686: Build against ea-nginx version v1.26.3

* Wed Aug 14 2024 Cory McIntire <cory@cpanel.net> - 6.0.23-2
- EA-12337: Build against ea-nginx version v1.26.2

* Thu Aug 01 2024 Cory McIntire <cory@cpanel.net> - 6.0.23-1
- EA-12307: ea-passenger-src was updated from v6.0.22 to v6.0.23

* Mon Jun 10 2024 Cory McIntire <cory@cpanel.net> - 6.0.22-2
- EA-12203: Build against ea-nginx version v1.26.1

* Sat May 18 2024 Cory McIntire <cory@cpanel.net> - 6.0.22-1
- EA-12161: ea-passenger-src was updated from v6.0.20 to v6.0.22

* Tue Apr 23 2024 Cory McIntire <cory@cpanel.net> - 6.0.20-6
- EA-12112: Build against ea-nginx version v1.26.0

* Mon Apr 22 2024 Cory McIntire <cory@cpanel.net> - 6.0.20-5
- EA-12100: Build against ea-nginx version 1.25.5 and update passenger version

* Wed Feb 14 2024 Cory McIntire <cory@cpanel.net> - 6.0.18-4
- EA-11973: Build against ea-nginx version v1.25.4

* Thu Oct 26 2023 Cory McIntire <cory@cpanel.net> - 6.0.18-3
- EA-11772: Build against ea-nginx version v1.25.3

* Thu Aug 24 2023 Cory McIntire <cory@cpanel.net> - 6.0.18-2
- EA-11631: Build against ea-nginx version v1.25.2

* Tue Jul 11 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 0.63-1
- ZC-10396: Create ea-nginx-passenger
