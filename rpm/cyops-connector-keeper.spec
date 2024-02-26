Name: cyops-connector-%{connector_name}
Prefix: /opt/%{name}
Version: %{_version}
Release: %{build_no}%{dist}
Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-root

Requires: cyops-integrations, lsof, cyops-api, cyops-connector-cyops_utilities >= 2.5.0

Summary: Fortinet %{connector_display_name} Connector
%description
Fortinet %{connector_display_name} Connector

#%global
%define integrations_dir /opt/cyops-integrations
%define integrations_dir_new /opt/cyops/configs
%define venv_name .env
%define venv_install_dir %{integrations_dir}/%{venv_name}
%define venv_bin %{venv_install_dir}/bin
%define venv_python %{venv_bin}/python3
%define venv_pip %{venv_python} %{venv_bin}/pip3 install
%define venv_site_packages %{venv_install_dir}/lib/python3.4/site-packages/

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}%{prefix}/
cp %{connector_name}.tgz %{buildroot}%{prefix}/
if [ -f compatibility.txt ]; then
    cp install.py %{buildroot}%{prefix}/
    cp compatibility.txt %{buildroot}%{prefix}/
fi
echo "compatibility_check is %{compatibility_check}"
%clean

%post
mkdir -p %{install_log_dir}
{
    set -x
    echo "Date: `date`"
    echo "%{name}: post"
    echo "============================================"

    # Install requirements.txt
    mod_version=`echo %{version} | sed 's/\./_/g'`
    connector_name_version=%{connector_name}_${mod_version}
    if [ -f %{integrations_dir_new}/integrations/connectors/${connector_name_version}/requirements.txt ]; then
        rm -rf ~/.cache/pip/
        export LC_ALL="en_US.UTF-8"
        sudo -u nginx %{venv_pip} -b ./tmp -r %{integrations_dir_new}/integrations/connectors/${connector_name_version}/requirements.txt --no-dependencies
    fi
    find %{buildroot} -name "RECORD" -exec rm -rf {} \;
    rm -rf ./tmp

    restorecon -R %{prefix}

    echo "============================================"
} >> %{install_log_dir}/%{install_log_file} 2>&1
# post ends here

%files
%{prefix}
%attr(0755, root, root) %{prefix}/%{connector_name}.tgz
%if "%{compatibility_check}" == "1"
%attr(0755, root, root) %{prefix}/install.py
%attr(0755, root, root) %{prefix}/compatibility.txt
%endif

