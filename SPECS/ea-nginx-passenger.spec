Name:           ea-nginx-passenger
Version:        6.0.18
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4552 for more details
%define release_prefix 1
Release:        %{release_prefix}%{?dist}.cpanel
Summary:        Provides passenger module for ea-nginx
License:        MIT
URL:            https://www.phusionpassenger.com
Group:          System Environment/Libraries
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:  ea-nginx-ngxdev
BuildRequires:  ea-passenger-src

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

%if 0%{?rhel} == 9
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: rubygem-rake
%else
BuildRequires: %{ruby_version}
BuildRequires: %{ruby_version}-rubygem-rake >= 0.8.1
BuildRequires: %{ruby_version}-rubygem-passenger
BuildRequires: %{ruby_version}-ruby-devel
%endif

Requires: ea-nginx
Requires: ea-passenger-runtime

Source1:  ea-nginx-passenger-module.conf

%description
This module provides Phusion Passenger app support for ea-nginx

%prep
set -x
cp -rf /opt/cpanel/ea-passenger-src/passenger-*/ .

%build
set -x

%if 0%{?rhel} == 8
export PATH=$PATH:/opt/cpanel/ea-ruby27/root/usr/bin
export WITH_CC_OPT="-I/opt/cpanel/ea-brotli/include -I/opt/cpanel/ea-passenger-src/passenger-release-%{version}/src"
export WITH_LD_OPT=-Wl,-rpath=/opt/cpanel/ea-brotli/lib
%endif

. /opt/cpanel/ea-nginx-ngxdev/set_NGINX_CONFIGURE_array.sh
./configure "${NGINX_CONFIGURE[@]}" \
    --add-dynamic-module=../passenger-release-%{version}/src/nginx_module \
%if 0%{?rhel} == 8
    --with-cc-opt="$WITH_CC_OPT" \
    --with-ld-opt="$WITH_LD_OPT" \
%endif

make

popd

%install
set -x 

if [ "$NAME" = "Ubuntu" ]; then
# This allows me to maintain this code in the SPEC file
# buildroot and libdir are wrong for Ubuntu

install -D %{SOURCE1} $DEB_INSTALL_ROOT/etc/nginx/conf.d/modules/ea-nginx-passenger-module.conf
install -D ./nginx-build/objs/ngx_http_passenger_module.so $DEB_INSTALL_ROOT/usr/lib64/nginx/modules/ngx_http_passenger_module.so
else
# We are CentOS
install -D %{SOURCE1} %{buildroot}/etc/nginx/conf.d/modules/ea-nginx-passenger-module.conf
install -D ./nginx-build/objs/ngx_http_passenger_module.so %{buildroot}%{_libdir}/nginx/modules/ngx_http_passenger_module.so
fi

%clean
rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
/etc/nginx/conf.d/modules/ea-nginx-passenger-module.conf
%attr(0755,root,root) %{_libdir}/nginx/modules/ngx_http_passenger_module.so

%changelog
* Tue Jul 11 2023 Brian Mendoza <brian.mendoza@cpanel.net> - 0.63-1
- ZC-10396: Create ea-nginx-passenger
