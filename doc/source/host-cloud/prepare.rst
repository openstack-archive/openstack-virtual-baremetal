Preparing the Host Cloud Environment
====================================

#. The ``ipxe`` directory contains tools for building an IPXE image which is used by the baremetal
   instances to begin provisioning over the network.

   To install the required build dependencies on a Fedora system::

       sudo dnf install -y gcc xorriso make qemu-img syslinux-nonlinux xz-devel

   It may be necessary to use the ``direct`` libguestfs backend::

       export LIBGUESTFS_BACKEND=direct

   To build the image, run the following from the root of the OVB repo::

       make -C ipxe

#. Upload an ipxe-boot image for the baremetal instances, for both UEFI boot and
   legacy BIOS boot::

    openstack image create --progress --disk-format raw --property os_shutdown_timeout=5 --file ipxe/ipxe-boot.img ipxe-boot
    openstack image create --progress --disk-format raw --property os_shutdown_timeout=5 --property hw_firmware_type=uefi --property hw_machine_type=q35 --file ipxe/ipxe-boot.img ipxe-boot-uefi

   .. note:: The path provided to ipxe-boot.qcow2 is relative to the root of
             the OVB repo.  If the command is run from a different working
             directory, the path will need to be adjusted accordingly.

   .. note:: os_shutdown_timeout=5 is to avoid server shutdown delays since
             since these servers won't respond to graceful shutdown requests.

#. Upload a CentOS 7 image for use as the base image::

    wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2

    glance image-create --name CentOS-7-x86_64-GenericCloud --disk-format qcow2 --container-format bare < CentOS-7-x86_64-GenericCloud.qcow2

#. (Optional) Create a pre-populated base BMC image.  This is a CentOS 7 image
   with the required packages for the BMC pre-installed.  This eliminates one
   potential point of failure during the deployment of an OVB environment
   because the BMC will not require any external network resources::

    wget https://repos.fedorapeople.org/repos/openstack-m/ovb/bmc-base.qcow2

    glance image-create --name bmc-base --disk-format qcow2 --container-format bare < bmc-base.qcow2

   To use this image, configure ``bmc_image`` in env.yaml to be ``bmc-base`` instead
   of the generic CentOS 7 image.

#. Create recommended flavors::

    nova flavor-create baremetal auto 8192 50 2
    nova flavor-create bmc auto 512 20 1

   These flavors can be customized if desired.  For large environments
   with many baremetal instances it may be wise to give the bmc flavor
   more memory.  A 512 MB BMC will run out of memory around 20 baremetal
   instances.

#. Source an rc file that will provide user credentials for the host cloud.

#. Add a Nova keypair to be injected into instances::

    nova keypair-add --pub-key ~/.ssh/id_rsa.pub default

#. (Optional) Configure quotas.  When running in a dedicated OVB cloud, it may
   be helpful to set some quotas to very large/unlimited values to avoid
   running out of quota when deploying multiple or large environments::

    neutron quota-update --security_group 1000
    neutron quota-update --port -1
    neutron quota-update --network -1
    neutron quota-update --subnet -1
    nova quota-update --instances -1 --cores -1 --ram -1 [tenant uuid]
