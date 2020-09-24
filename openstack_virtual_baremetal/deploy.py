#!/usr/bin/env python
# Copyright 2016 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import sys
import time
import yaml

from heatclient.common import template_utils
import os_client_config

# TODO(sshnaidm): To make this python3 friendly with relative imports
try:
    from openstack_virtual_baremetal import auth
except ImportError:
    import auth


def _parse_args():
    parser = argparse.ArgumentParser(description='Deploy an OVB environment')
    parser.add_argument(
        '--env', '-e',
        help='Path to Heat environment file describing the OVB '
             'environment to be deployed. Default: %(default)s',
        action='append',
        default=[])
    parser.add_argument(
        '--id',
        help='Identifier to add to all resource names. The '
             'resulting names will look like undercloud-ID or '
             'baremetal-ID. By default no changes will be made to '
             'the resource names. If an id is specified, a new '
             'environment file will be written to env-ID.yaml. ')
    parser.add_argument(
        '--name',
        help='Name for the Heat stack to be created. Defaults '
             'to "baremetal" in a standard deployment. If '
             '--quintupleo is specified then the default is '
             '"quintupleo".')
    parser.add_argument(
        '--quintupleo',
        help='Deploy a full environment suitable for TripleO '
             'development.',
        action='store_true',
        default=False)
    parser.add_argument(
        '--role',
        help='Additional environment file describing a '
             'secondary role to be deployed alongside the '
             'primary one described in the main environment.',
        action='append',
        default=[])
    parser.add_argument(
        '--poll',
        help='Poll until the Heat stack(s) are complete. '
             'Automatically enabled when multiple roles are '
             'deployed.',
        action='store_true',
        default=False)
    return parser.parse_args()


def _process_args(args):
    if args.id:
        if not args.quintupleo:
            raise RuntimeError('--id requires --quintupleo')
        id_env = 'env-%s.yaml' % args.id
        if id_env in args.env:
            raise ValueError('Input env file "%s" would be overwritten by ID '
                             'env file.  Either rename the input file or '
                             'change the deploy ID.' % id_env)
    if args.role and not args.quintupleo:
        raise RuntimeError('--role requires --quintupleo')

    # NOTE(bnemec): We changed the way the --env parameter works such that the
    # default is no longer 'env.yaml' but instead an empty list.  However, for
    # compatibility we need to maintain the ability to default to env.yaml
    # if --env is not explicitly specified.
    if not args.env:
        args.env = ['env.yaml']
    if args.name:
        stack_name = args.name
    else:
        stack_name = 'baremetal'
        if args.quintupleo:
            stack_name = 'quintupleo'
    if not args.quintupleo:
        stack_template = 'templates/virtual-baremetal.yaml'
    else:
        stack_template = 'templates/quintupleo.yaml'
    return stack_name, stack_template


def _add_identifier(env_data, name, identifier, default=None):
    """Append identifier to the end of parameter name in env_data

    Look for ``name`` in the ``parameter_defaults`` key of ``env_data`` and
    append '-``identifier``' to it.
    """
    value = env_data['parameter_defaults'].get(name)
    if value is None:
        value = default
    if value is None:
        raise RuntimeError('No base value found when adding id')
    if identifier:
        value = '%s-%s' % (value, identifier)
    env_data['parameter_defaults'][name] = value


def _build_env_data(env_paths):
    """Merge env data from the provided paths

    Given a list of files in env_paths, merge the contents of all those
    environment files and return the results.

    :param env_paths: A list of env files to operate on.
    :returns: A dict containing the merged contents of the provided files.
    """
    _, env_data = template_utils.process_multiple_environments_and_files(
        env_paths)
    return env_data


def _generate_id_env(args):
    env_data = _build_env_data(args.env)
    _add_identifier(env_data, 'provision_net', args.id, default='provision')
    _add_identifier(env_data, 'provision_net2', args.id, default='provision2')
    _add_identifier(env_data, 'provision_net3', args.id, default='provision3')
    _add_identifier(env_data, 'public_net', args.id, default='public')
    _add_identifier(env_data, 'baremetal_prefix', args.id, default='baremetal')
    role = env_data['parameter_defaults'].get('role')
    if role:
        _add_identifier(env_data, 'baremetal_prefix', role)
    _add_identifier(env_data, 'bmc_prefix', args.id, default='bmc')
    _add_identifier(env_data, 'undercloud_name', args.id, default='undercloud')
    _add_identifier(env_data, 'dhcrelay_prefix', args.id, default='dhcrelay')
    _add_identifier(env_data, 'radvd_prefix', args.id, default='radvd')
    _add_identifier(env_data, 'overcloud_internal_net', args.id,
                    default='internal')
    _add_identifier(env_data, 'overcloud_storage_net', args.id,
                    default='storage')
    _add_identifier(env_data, 'overcloud_storage_mgmt_net', args.id,
                    default='storage_mgmt')
    _add_identifier(env_data, 'overcloud_tenant_net', args.id,
                    default='tenant')
    # TODO(bnemec): Network names should be parameterized so we don't have to
    # hardcode them into deploy.py like this.
    _add_identifier(env_data, 'overcloud_internal_net2', args.id,
                    default='overcloud_internal2')
    _add_identifier(env_data, 'overcloud_storage_net2', args.id,
                    default='overcloud_storage2')
    _add_identifier(env_data, 'overcloud_storage_mgmt_net2', args.id,
                    default='overcloud_storage_mgmt2')
    _add_identifier(env_data, 'overcloud_tenant_net2', args.id,
                    default='overcloud_tenant2')
    _add_identifier(env_data, 'overcloud_internal_router', args.id,
                    default='internal_router')
    _add_identifier(env_data, 'overcloud_storage_router', args.id,
                    default='storage_router')
    _add_identifier(env_data, 'overcloud_storage_mgmt_router', args.id,
                    default='storage_mgmt_router')
    _add_identifier(env_data, 'overcloud_tenant_router', args.id,
                    default='tenant_router')
    _add_identifier(env_data, 'provision_router_name', args.id,
                    default='provision_router')

    # We don't modify any resource_registry entries, and because we may be
    # writing the new env file to a different path it can break relative paths
    # in the resource_registry.
    env_data.pop('resource_registry', None)
    env_path = 'env-%s.yaml' % args.id
    with open(env_path, 'w') as f:
        yaml.safe_dump(env_data, f, default_flow_style=False)
    return args.env + [env_path]


def _validate_env(args, env_paths):
    """Check for invalid environment configurations

    :param args: Argparse args.
    :param env_paths: Path(s) of the environment file(s) to validate.
    """
    if not args.id:
        env_data = _build_env_data(env_paths)
        role = env_data.get('parameter_defaults', {}).get('role')
        prefix = env_data['parameter_defaults']['baremetal_prefix']
        if role and prefix.endswith('-' + role):
            raise RuntimeError('baremetal_prefix ends with role name.  This '
                               'will break build-nodes-json.  Please choose '
                               'a different baremetal_prefix or role name.')
    for path in env_paths:
        if 'port-security.yaml' in path:
            print('WARNING: port-security environment file detected. '
                  'port-security is now the default. The existing '
                  'port-security environment files are deprecated and may be '
                  'removed in the future. Please use the environment files '
                  'without "port-security" in their filename instead.'
                  )


def _get_heat_client():
    return os_client_config.make_client('orchestration',
                                        cloud=auth.OS_CLOUD)


def _deploy(stack_name, stack_template, env_paths, poll):
    hclient = _get_heat_client()

    template_files, template = template_utils.get_template_contents(
        stack_template)
    env_files, env = template_utils.process_multiple_environments_and_files(
        ['templates/resource-registry.yaml'] + env_paths)
    all_files = {}
    all_files.update(template_files)
    all_files.update(env_files)
    # NOTE(bnemec): Unfortunately, we can't pass this in as parameter_default
    # because the Heat API doesn't accept parameter_defaults.
    parameters = {'cloud_data': auth._cloud_json()}

    hclient.stacks.create(stack_name=stack_name,
                          template=template,
                          environment=env,
                          files=all_files,
                          parameters=parameters)

    print('Deployment of stack "%s" started.' % stack_name)
    if poll:
        _poll_stack(stack_name, hclient)


def _poll_stack(stack_name, hclient):
    """Poll status for stack_name until it completes or fails"""
    print('Waiting for stack to complete', end="")
    done = False
    while not done:
        print('.', end="")
        # By the time we get here we know Heat was up at one point because
        # we were able to start the stack create.  Therefore, we can
        # reasonably guess that any errors from this call are going to be
        # transient.
        try:
            stack = hclient.stacks.get(stack_name, resolve_outputs=False)
        except Exception as e:
            # Print the error so the user can determine whether they need
            # to cancel the deployment, but keep trying otherwise.
            print('WARNING: Exception occurred while polling stack: %s' % e)
            time.sleep(10)
            continue
        sys.stdout.flush()
        if stack.status == 'COMPLETE':
            print('Stack %s created successfully' % stack_name)
            done = True
        elif stack.status == 'FAILED':
            print(stack.to_dict().get('stack_status_reason'))
            raise RuntimeError('Failed to create stack %s' % stack_name)
        else:
            time.sleep(10)


# Abstract out the role file interactions for easier unit testing
def _load_role_data(base_envs, role_file, args):
    base_data = _build_env_data(base_envs)
    with open(role_file) as f:
        role_data = yaml.safe_load(f)
    orig_data = _build_env_data(args.env)
    return base_data, role_data, orig_data


def _write_role_file(role_env, role_file):
    with open(role_file, 'w') as f:
        yaml.safe_dump(role_env, f, default_flow_style=False)


def _process_role(role_file, base_envs, stack_name, args):
    """Merge a partial role env with the base env

    :param role: Filename of an environment file containing the definition
        of the role.
    :param base_envs: Filename(s) of the environment file(s) used to deploy the
        stack containing shared resources such as the undercloud and
        networks.
    :param stack_name: Name of the stack deployed using base_envs.
    :param args: The command-line arguments object from argparse.
    """
    base_data, role_data, orig_data = _load_role_data(base_envs, role_file,
                                                      args)
    inherited_keys = ['baremetal_image', 'bmc_flavor', 'bmc_image',
                      'external_net', 'key_name', 'os_auth_url',
                      'os_password', 'os_tenant', 'os_user',
                      'private_net', 'provision_net', 'public_net',
                      'overcloud_internal_net', 'overcloud_storage_mgmt_net',
                      'overcloud_storage_net', 'overcloud_tenant_net',
                      ]
    # Parameters that are inherited but can be overridden by the role
    allowed_parameter_keys = ['baremetal_image', 'bmc_flavor', 'key_name',
                              'provision_net', 'overcloud_internal_net',
                              'overcloud_storage_net',
                              'overcloud_storage_mgmt_net',
                              'overcloud_tenant_net',
                              ]
    allowed_registry_keys = ['OS::OVB::BaremetalPorts', 'OS::OVB::BMCPort',
                             'OS::OVB::UndercloudNetworks', 'OS::OVB::BMC',
                             ]
    # NOTE(bnemec): Not sure what purpose this serves. Can probably be removed.
    role_env = role_data
    # resource_registry is intentionally omitted as it should not be inherited
    role_env.setdefault('parameter_defaults', {}).update({
        k: v for k, v in base_data.get('parameter_defaults', {}).items()
        if k in inherited_keys and
        (k not in role_env.get('parameter_defaults', {}) or
         k not in allowed_parameter_keys)
    })
    # Most of the resource_registry should not be included in role envs.
    # Only allow specific entries that may be needed.
    role_env.setdefault('resource_registry', {})
    role_env['resource_registry'] = {
        k: v for k, v in role_env['resource_registry'].items()
        if k in allowed_registry_keys}
    role_reg = role_env['resource_registry']
    base_reg = base_data['resource_registry']
    for k in allowed_registry_keys:
        if k not in role_reg and k in base_reg:
            role_reg[k] = base_reg[k]
    # We need to start with the unmodified prefix
    base_prefix = orig_data['parameter_defaults']['baremetal_prefix']
    # But we do need to add the id if one is in use
    if args.id:
        base_prefix += '-%s' % args.id
    bmc_prefix = base_data['parameter_defaults']['bmc_prefix']
    role = role_data['parameter_defaults']['role']
    if '_' in role:
        raise RuntimeError('_ character not allowed in role name "%s".' % role)
    role_env['parameter_defaults']['baremetal_prefix'] = ('%s-%s' %
                                                          (base_prefix, role))
    role_env['parameter_defaults']['bmc_prefix'] = '%s-%s' % (bmc_prefix, role)
    # At this time roles are only attached to a single set of networks, so
    # we use just the primary network parameters.

    def maybe_add_id(role_env, name, args):
        """Add id only if one is not already present

        When we inherit network names, they will already have the id present.
        However, if the user overrides the network name (for example, when
        using multiple routed networks) then it should not have the id.
        We can detect which is the case by looking at whether the name already
        ends with -id.
        """
        if (args.id and
                not role_env['parameter_defaults'].get(name, '')
                                                  .endswith('-' + args.id)):
            _add_identifier(role_env, name, args.id)

    maybe_add_id(role_env, 'provision_net', args)
    maybe_add_id(role_env, 'overcloud_internal_net', args)
    maybe_add_id(role_env, 'overcloud_storage_net', args)
    maybe_add_id(role_env, 'overcloud_storage_mgmt_net', args)
    maybe_add_id(role_env, 'overcloud_tenant_net', args)
    role_env['parameter_defaults']['networks'] = {
        'private': role_env['parameter_defaults']['private_net'],
        'provision': role_env['parameter_defaults']['provision_net'],
        'public': role_env['parameter_defaults']['public_net'],
    }
    role_file = 'env-%s-%s.yaml' % (stack_name, role)
    _write_role_file(role_env, role_file)
    return role_file, role


def _deploy_roles(stack_name, args, env_paths):
    for r in args.role:
        role_env, role_name = _process_role(r, env_paths, stack_name, args)
        _deploy(stack_name + '-%s' % role_name,
                'templates/virtual-baremetal.yaml',
                [role_env], poll=True)


def main():
    args = _parse_args()
    stack_name, stack_template = _process_args(args)
    env_paths = args.env
    if args.id:
        env_paths = _generate_id_env(args)
    _validate_env(args, env_paths)
    poll = args.poll
    if args.role:
        poll = True
    _deploy(stack_name, stack_template, env_paths, poll=poll)
    _deploy_roles(stack_name, args, env_paths)


if __name__ == '__main__':
    main()
