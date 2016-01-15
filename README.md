 IM - Infrastructure Manager (With TOSCA Support)
=================================================

* Version ![PyPI](https://img.shields.io/pypi/v/im.svg)
* PyPI ![PypI](https://img.shields.io/pypi/dm/IM.svg)

IM is a tool that deploys complex and customized virtual infrastructures on IaaS
Cloud deployments (such as AWS, OpenStack, etc.). It eases the access and the
usability of IaaS clouds by automating the VMI (Virtual Machine Image)
selection, deployment, configuration, software installation, monitoring and
update of the virtual infrastructure. It supports APIs from a large number of virtual
platforms, making user applications cloud-agnostic. In addition it integrates a
contextualization system to enable the installation and configuration of all the
user required applications providing the user with a fully functional
infrastructure.

Read the documentation and more at http://www.grycap.upv.es/im.

There is also an Infrastructure Manager youtube channel with a set of videos with demos
of the functionality of the platform: [YouTube IM channel](https://www.youtube.com/channel/UCF16QmMHlRNtsC-0Cb2d8fg)


1. INSTALLATION
===============

1.1 REQUISITES
--------------

IM is based on Python, so Python 2.6 or higher runtime and standard library must
be installed in the system.

 + The Python Lex & Yacc library (http://www.dabeaz.com/ply/), typically available
   as the 'python-ply' package.

 + The paramiko ssh2 protocol library for python version 1.14 or later
(http://www.lag.net/paramiko/), typically available as the 'python-paramiko' package.

 + The YAML library for Python, typically available as the 'python-yaml' or 'PyYAML' package.

 + The SOAPpy library for Python, typically available as the 'python-soappy' or 'SOAPpy' package.
 
 + The Netaddr library for Python, typically available as the 'python-netaddr' package.
 
 + The boto library version 2.29 or later
   must be installed (http://boto.readthedocs.org/en/latest/).

 + The apache-libcloud library version 0.18 or later
   must be installed (http://libcloud.apache.org/).
 
 + The TOSCA-Parser library for Python. Currently it must be used the INDIGO version located at
   https://github.com/indigo-dc/tosca-parser but we are working to improve the mainstream version
   to enable to use it with the IM. 

 + Ansible (http://www.ansibleworks.com/) to configure nodes in the infrastructures.
   In particular, Ansible 1.4.2+ must be installed.
   To ensure the functionality the following values must be set in the ansible.cfg file (usually found in /etc/ansible/):

```
[defaults]
transport  = smart
host_key_checking = False
sudo_user = root
sudo_exe = sudo

[paramiko_connection]

record_host_keys=False

[ssh_connection]

# Only in systems with OpenSSH support to ControlPersist
ssh_args = -o ControlMaster=auto -o ControlPersist=900s
# In systems with older versions of OpenSSH (RHEL 6, CentOS 6, SLES 10 or SLES 11) 
#ssh_args =
pipelining = True
```

1.2 OPTIONAL PACKAGES
---------------------

In case of using the SSL secured version of the XMLRPC API the SpringPython
framework (http://springpython.webfactional.com/) must be installed.

In case of using the REST API the Bottle framework
(http://bottlepy.org/) must be installed.

In case of using the SSL secured version of the REST API the CherryPy Web
framework (http://www.cherrypy.org/) must be installed.

1.3 INSTALLING
--------------

First install the requirements:

On Debian Systems:
```
$ apt-get -y install git python-setuptools python-dev gcc python-soappy python-pip python-pbr python-dateutil
```

On RedHat Systems:
```
$ yum remove python-paramiko python-crypto
$ yum -y install git python-setuptools python-devel gcc SOAPpy python-dateutil python-six python-requests
$ easy_install pip
$ pip install  pbr 
```

Then install the TOSCA parser:

```
$ cd /tmp
$ git clone --recursive https://github.com/indigo-dc/tosca-parser.git
$ cd tosca-parser
$ python setup.py install
```

Finally install the IM service:

```
$ cd /tmp
$ git clone --recursive https://github.com/indigo-dc/im.git
$ cd im
$ python setup.py install
```


1.4 CONFIGURATION
-----------------

In case that you want the IM service to be started at boot time, you must
execute the next set of commands:

On Debian Systems:

```
$ chkconfig im on
```

Or for newer systems like ubuntu 14.04:

```
$ sysv-rc-conf im on
```

On RedHat Systems:

```
$ update-rc.d im start 99 2 3 4 5 . stop 05 0 1 6 .
```

Or you can do it manually:

```
$ ln -s /etc/init.d/im /etc/rc2.d/S99im
$ ln -s /etc/init.d/im /etc/rc3.d/S99im
$ ln -s /etc/init.d/im /etc/rc5.d/S99im
$ ln -s /etc/init.d/im /etc/rc1.d/K05im
$ ln -s /etc/init.d/im /etc/rc6.d/K05im
```

Adjust the installation path by setting the IMDAEMON variable at /etc/init.d/im
to the path where the IM im_service.py file is installed (e.g. /usr/local/im/im_service.py),
or set the name of the script file (im_service.py) if the file is in the PATH
(pip puts the im_service.py file in the PATH as default).

Check the parameters in $IM_PATH/etc/im.cfg or /etc/im/im.cfg. Please pay attention
to the next configuration variables, as they are the most important

DATA_FILE - must be set to the full path where the IM data file will be created
         (e.g. /usr/local/im/inf.dat). Be careful if you have two different instances
         of the IM service running in the same machine!!.

CONTEXTUALIZATION_DIR - must be set to the full path where the IM contextualization files
		are located. In case of using pip installation the default value is correct
		(/usr/share/im/contextualization) in case of installing from sources set to
		$IM_PATH/contextualization (e.g. /usr/local/im/contextualization)

### 1.4.1 SECURITY

Security is disabled by default. Please notice that someone with local network access can "sniff" the traffic and
get the messages with the IM with the authorisation data with the cloud providers.

Security can be activated both in the XMLRPC and REST APIs. Setting this variables:

XMLRCP_SSL = True

or

REST_SSL = True

And then set the variables: XMLRCP_SSL_* or REST_SSL_* to your certificates paths.

2. DOCKER IMAGE
===============

A Docker image named `indigodatacloud/im` has been created to make easier the deployment of an IM service using the 
default configuration. Information about this image can be found here: https://hub.docker.com/r/indigodatacloud/im/.

How to launch the IM service using docker:

```sh
sudo docker run -d -p 8899:8899 --name im indigodatacloud/im 
```
