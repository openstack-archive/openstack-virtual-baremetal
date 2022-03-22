#!/bin/bash
set -x

centos_ver=$(rpm --eval %{centos_ver})

if [ "$centos_ver" == "7" ] ; then
    curl -o /etc/yum.repos.d/delorean.repo https://trunk.rdoproject.org/centos7/current/delorean.repo
    yum install -y python2-tripleo-repos
    tripleo-repos current-tripleo
    yum install -y python-crypto python2-novaclient python2-neutronclient python2-pyghmi os-net-config python2-os-client-config python2-openstackclient
else
    set +x
    $signal_command --data-binary '{"status": "FAILURE"}'
    echo "Unsupported CentOS version $centos_ver"
    exit 1
fi

cat <<EOF >/usr/local/bin/openstackbmc
$openstackbmc_script
EOF
chmod +x /usr/local/bin/openstackbmc

# Configure clouds.yaml so we can authenticate to the host cloud
mkdir -p ~/.config/openstack
# Passing this as an argument is problematic because it has quotes inline that
# cause syntax errors.  Reading from a file should be easier.
cat <<'EOF' >/tmp/bmc-cloud-data
$cloud_data
EOF
python -c 'import json
import sys
import yaml
with open("/tmp/bmc-cloud-data") as f:
    data=json.loads(f.read())
clouds={"clouds": {"host_cloud": data}}
print(yaml.safe_dump(clouds, default_flow_style=False))' > ~/.config/openstack/clouds.yaml
rm -f /tmp/bmc-cloud-data
export OS_CLOUD=host_cloud

# python script do query the cloud and write out the bmc services/configs
$(command -v python3 || command -v python2) <<EOF
import json
import openstack
import os
import sys

cache_status = ''
if not $bmc_use_cache:
    cache_status = '--cache-status'

conn = openstack.connect(cloud='host_cloud')
print('Fetching private network')
items = conn.network.networks(name='$private_net')
private_net = next(items, None)

print('Fetching private subnet')
private_subnet = conn.network.find_subnet(private_net.subnet_ids[0])

if not private_subnet:
    print('[ERROR] Could not find private subnet')
    sys.exit(1)

default_gw = private_subnet.gateway_ip
prefix_len = private_subnet.cidr.split('/')[1]
mtu = private_net.mtu

os_net_config = {
  'network_config': [{
    'type': 'interface',
    'name': 'eth0',
    'use_dhcp': False,
    'mtu': mtu,
    'routes': [{
      'default': True,
      'next_hop': default_gw,
    }],
    'addresses': [
      { 'ip_netmask': '$bmc_utility/{}'.format(prefix_len) }
    ]
  }]
}

os_net_config_unit = """
[Unit]
Description=config-bmc-ips Service
Requires=network.target
After=network.target

[Service]
ExecStart=/bin/os-net-config -c /etc/os-net-config/config.json -v
Type=oneshot
User=root
StandardOutput=kmsg+console
StandardError=inherit

[Install]
WantedBy=multi-user.target
"""

print('Writing out config-bmc-ips.service')
with open('/usr/lib/systemd/system/config-bmc-ips.service', 'w') as f:
    f.write(os_net_config_unit)

print('Fetching bm ports')
bmc_port_names = [('$bmc_prefix_{}'.format(x), '$bm_prefix_{}'.format(x)) for x in range(0, $bm_node_count)]
bmc_ports = {}
for (bmc_port_name, bm_port_name) in bmc_port_names:
    print('Finding {} port'.format(bmc_port_name))
    bmc_ports[bmc_port_name] = conn.network.find_port(bmc_port_name)
    print('Finding {} port'.format(bm_port_name))
    bmc_ports[bm_port_name] = conn.network.find_port(bm_port_name)


unit_template = """
[Unit]
Description=openstack-bmc {port_name} Service
Requires=config-bmc-ips.service
After=config-bmc-ips.service

[Service]
ExecStart=/usr/local/bin/openstackbmc --os-cloud host_cloud --instance {port_instance} --address {port_ip} {cache_status}
Restart=always

User=root
StandardOutput=kmsg+console
StandardError=inherit

[Install]
WantedBy=multi-user.target
"""
for (bmc_port_name, bm_port_name) in bmc_port_names:
    port_name = bm_port_name
    unit_file = os.path.join('/usr/lib/systemd/system', 'openstack-bmc-{}.service'.format(port_name))
    device_id = bmc_ports[bm_port_name].device_id
    port = bmc_ports[bmc_port_name]
    if isinstance(port.fixed_ips, list):
        port_ip = port.fixed_ips[0].get('ip_address')
    else:
        # TODO: test older openstacksdk
        port_ip = port.fixed_ips.split('\'')[1]

    print('Writing out {}'.format(unit_file))
    with open(unit_file, "w") as unit:
        unit.write(unit_template.format(port_name=port_name,
                                        port_instance=device_id,
                                        port_ip=port_ip,
                                        cache_status=cache_status))
    addr = { 'ip_netmask': '{}/{}'.format(port_ip, prefix_len) }
    os_net_config['network_config'][0]['addresses'].append(addr)


if not os.path.isdir('/etc/os-net-config'):
    os.mkdir('/etc/os-net-config')

print('Writing /etc/os-net-config/config.json')
with open('/etc/os-net-config/config.json', 'w') as f:
    json.dump(os_net_config, f)

EOF
# reload systemd
systemctl daemon-reload

# enable and start bmc ip service
systemctl enable config-bmc-ips
systemctl start config-bmc-ips

# enable bmcs
for i in $(seq 1 $bm_node_count)
do
    unit="openstack-bmc-$bm_prefix_$(($i-1)).service"
    systemctl enable $unit
    systemctl start $unit
done

sleep 5

if ! systemctl is-active openstack-bmc-* >/dev/null
then
    systemctl status openstack-bmc-*
    set +x
    $signal_command --data-binary '{"status": "FAILURE"}'
    echo "********** $unit failed to start **********"
    exit 1
fi
set +x
$signal_command --data-binary '{"status": "SUCCESS"}'

