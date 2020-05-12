Sample Environment Index
========================

Deploy with All Networks Enabled and Two Public Interfaces
----------------------------------------------------------

**File:** environments/all-networks-public-bond.yaml

**Description:** Deploy an OVB stack that adds interfaces for all the standard TripleO
network isolation networks.  This version will deploy duplicate
public network interfaces on the baremetal instances so that the
public network can be configured as a bond.


Deploy with All Networks Enabled
--------------------------------

**File:** environments/all-networks.yaml

**Description:** Deploy an OVB stack that adds interfaces for all the standard TripleO
network isolation networks.


Base Configuration Options for Extra Nodes with All Ports Open
--------------------------------------------------------------

**File:** environments/base-extra-node-all.yaml

**Description:** Configuration options that need to be set when deploying an OVB
environment with extra undercloud-like nodes.  This environment
should be used like a role file, but will deploy an undercloud-like
node instead of more baremetal nodes.


Base Configuration Options for Extra Nodes
------------------------------------------

**File:** environments/base-extra-node.yaml

**Description:** Configuration options that need to be set when deploying an OVB
environment with extra undercloud-like nodes.  This environment
should be used like a role file, but will deploy an undercloud-like
node instead of more baremetal nodes.


Base Configuration Options for Secondary Roles
----------------------------------------------

**File:** environments/base-role.yaml

**Description:** Configuration options that need to be set when deploying an OVB
environment that has multiple roles.


Base Configuration Options
--------------------------

**File:** environments/base.yaml

**Description:** Basic configuration options needed for all OVB environments

Enable Instance Status Caching in BMC
-------------------------------------

**File:** environments/bmc-use-cache.yaml

**Description:** Enable caching of instance status in the BMC.  This should reduce load on
the host cloud, but at the cost of potential inconsistency if the state
of a baremetal instance is changed without using the BMC.


Boot Baremetal Instances from Volume
------------------------------------

**File:** environments/boot-baremetal-from-volume.yaml

**Description:** Boot the baremetal instances from Cinder volumes instead of
ephemeral storage.


Boot Undercloud and Baremetal Instances from Volume
---------------------------------------------------

**File:** environments/boot-from-volume.yaml

**Description:** Boot the undercloud and baremetal instances from Cinder volumes instead of
ephemeral storage.


Boot Undercloud Instance from Volume
------------------------------------

**File:** environments/boot-undercloud-from-volume.yaml

**Description:** Boot the undercloud instance from a Cinder volume instead of
ephemeral storage.


Create a Private Network
------------------------

**File:** environments/create-private-network.yaml

**Description:** Create the private network as part of the OVB stack instead of using an
existing one.


Disable BMC
-----------

**File:** environments/disable-bmc.yaml

**Description:** Deploy a stack without a BMC. This will obviously make it impossible to
control the instances via IPMI. It will also prevent use of
ovb-build-nodes-json because there will be no BMC addresses.


Configuration for router advertisement daemon (radvd)
-----------------------------------------------------

**File:** environments/ipv6-radvd-configuration.yaml

**Description:** Contains the available parameters that need to be configured when using
a IPv6 network. Requires the ipv6-radvd.yaml environment.


Enable router advertisement daemon (radvd)
------------------------------------------

**File:** environments/ipv6-radvd.yaml

**Description:** Deploy the stack with a router advertisement daemon running for the
provisioning network.


Public Network External Router
------------------------------

**File:** environments/public-router.yaml

**Description:** Deploy a router that connects the public and external networks. This
allows the public network to be used as a gateway instead of routing all
traffic through the undercloud.


Disable the Undercloud in a QuintupleO Stack
--------------------------------------------

**File:** environments/quintupleo-no-undercloud.yaml

**Description:** Deploy a QuintupleO environment, but do not create the undercloud
instance.


Configuration for Routed Networks
---------------------------------

**File:** environments/routed-networks-configuration.yaml

**Description:** Contains the available parameters that need to be configured when using
a routed networks environment. Requires the routed-networks.yaml or
routed-networks-ipv6.yaml environment.


Enable Routed Networks IPv6
---------------------------

**File:** environments/routed-networks-ipv6.yaml

**Description:** Enable use of routed IPv6 networks, where there may be multiple separate
networks connected with a router, router advertisement daemon (radvd),
and DHCP relay. Do not pass any other network configuration environments
after this one or they may override the changes made by this environment.
When this environment is in use, the routed-networks-configuration
environment should usually be included as well.


Base Role Configuration for Routed Networks
-------------------------------------------

**File:** environments/routed-networks-role.yaml

**Description:** A base role environment that contains the necessary parameters for
deploying with routed networks.


Enable Routed Networks
----------------------

**File:** environments/routed-networks.yaml

**Description:** Enable use of routed networks, where there may be multiple separate
networks connected with a router and DHCP relay. Do not pass any other
network configuration environments after this one or they may override
the changes made by this environment. When this environment is in use,
the routed-networks-configuration environment should usually be
included as well.


Assign the Undercloud an Existing Floating IP
---------------------------------------------

**File:** environments/undercloud-floating-existing.yaml

**Description:** When deploying the undercloud, assign it an existing floating IP instead
of creating a new one.


Do Not Assign a Floating IP to the Undercloud
---------------------------------------------

**File:** environments/undercloud-floating-none.yaml

**Description:** When deploying the undercloud, do not assign a floating ip to it.


