# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2011 OpenStack, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import httplib2
import urlparse

from novaclient import client as base_client
from novaclient.v1_1 import client
from tests import fakes


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        client.Client.__init__(self, 'username', 'password',
                               'project_id', 'auth_url',
                               extensions=kwargs.get('extensions'))
        self.client = FakeHTTPClient(**kwargs)


class FakeHTTPClient(base_client.HTTPClient):

    def __init__(self, **kwargs):
        self.username = 'username'
        self.password = 'password'
        self.auth_url = 'auth_url'
        self.callstack = []

    def _cs_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        # Call the method
        args = urlparse.parse_qsl(urlparse.urlparse(url)[4])
        kwargs.update(args)
        munged_url = url.rsplit('?', 1)[0]
        munged_url = munged_url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')

        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected fakes method name: %s' %
                                 (method, url, callback))

        # Note the call
        self.callstack.append((method, url, kwargs.get('body', None)))

        status, body = getattr(self, callback)(**kwargs)
        if hasattr(status, 'items'):
            return httplib2.Response(status), body
        else:
            return httplib2.Response({"status": status}), body

    #
    # agents
    #

    def get_os_agents(self, **kw):
        hypervisor = kw.get('hypervisor', 'kvm')
        return (200, {'agents':
                    [{'hypervisor': hypervisor,
                      'os': 'win',
                     'architecture': 'x86',
                     'version': '7.0',
                     'url': 'xxx://xxxx/xxx/xxx',
                     'md5hash': 'add6bb58e139be103324d04d82d8f545',
                     'id': 1},
                    {'hypervisor': hypervisor,
                     'os': 'linux',
                     'architecture': 'x86',
                     'version': '16.0',
                     'url': 'xxx://xxxx/xxx/xxx1',
                     'md5hash': 'add6bb58e139be103324d04d82d8f546',
                     'id': 2},
                    ]})

    def post_os_agents(self, body):
        return (200, {'agent': {
                          'url': '/xxx/xxx/xxx',
                          'hypervisor': body['agent']['hypervisor'],
                          'md5hash': 'add6bb58e139be103324d04d82d8f546',
                          'version': '7.0',
                          'architecture': 'x86',
                          'os': 'win',
                          'id': 1}})

    def delete_os_agents_1(self, **kw):
        return (202, None)

    def put_os_agents_1(self, body, **kw):
        return (200, {"agent": {
                           "url": "/yyy/yyyy/yyyy",
                           "version": "8.0",
                           "md5hash": "add6bb58e139be103324d04d82d8f546",
                           'id': 1}})

    #
    # List all extensions
    #

    def get_extensions(self, **kw):
        exts = [
            {
                "alias": "NMN",
                "description": "Multiple network support",
                "links": [],
                "name": "Multinic",
                "namespace": ("http://docs.openstack.org/"
                              "compute/ext/multinic/api/v1.1"),
                "updated": "2011-06-09T00:00:00+00:00"
            },
            {
                "alias": "OS-DCF",
                "description": "Disk Management Extension",
                "links": [],
                "name": "DiskConfig",
                "namespace": ("http://docs.openstack.org/"
                              "compute/ext/disk_config/api/v1.1"),
                "updated": "2011-09-27T00:00:00+00:00"
            },
            {
                "alias": "OS-EXT-SRV-ATTR",
                "description": "Extended Server Attributes support.",
                "links": [],
                "name": "ExtendedServerAttributes",
                "namespace": ("http://docs.openstack.org/"
                              "compute/ext/extended_status/api/v1.1"),
                "updated": "2011-11-03T00:00:00+00:00"
            },
            {
                "alias": "OS-EXT-STS",
                "description": "Extended Status support",
                "links": [],
                "name": "ExtendedStatus",
                "namespace": ("http://docs.openstack.org/"
                              "compute/ext/extended_status/api/v1.1"),
                "updated": "2011-11-03T00:00:00+00:00"
            },
        ]
        return (200, {
            "extensions": exts,
        })

    #
    # Limits
    #

    def get_limits(self, **kw):
        return (200, {"limits": {
            "rate": [
                {
                    "uri": "*",
                    "regex": ".*",
                    "limit": [
                        {
                            "value": 10,
                            "verb": "POST",
                            "remaining": 2,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        },
                        {
                            "value": 10,
                            "verb": "PUT",
                            "remaining": 2,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        },
                        {
                            "value": 100,
                            "verb": "DELETE",
                            "remaining": 100,
                            "unit": "MINUTE",
                            "next-available": "2011-12-15T22:42:45Z"
                        }
                    ]
                },
                {
                    "uri": "*/servers",
                    "regex": "^/servers",
                    "limit": [
                        {
                            "verb": "POST",
                            "value": 25,
                            "remaining": 24,
                            "unit": "DAY",
                            "next-available": "2011-12-15T22:42:45Z"
                        }
                    ]
                }
            ],
            "absolute": {
                "maxTotalRAMSize": 51200,
                "maxServerMeta": 5,
                "maxImageMeta": 5,
                "maxPersonality": 5,
                "maxPersonalitySize": 10240
            },
        },
    })

    #
    # Servers
    #

    def get_servers(self, **kw):
        return (200, {"servers": [
            {'id': 1234, 'name': 'sample-server'},
            {'id': 5678, 'name': 'sample-server2'}
        ]})

    def get_servers_detail(self, **kw):
        return (200, {"servers": [
            {
                "id": 1234,
                "name": "sample-server",
                "image": {
                    "id": 2,
                    "name": "sample image",
                },
                "flavor": {
                    "id": 1,
                    "name": "256 MB Server",
                },
                "hostId": "e4d909c290d0fb1ca068ffaddf22cbd0",
                "status": "BUILD",
                "progress": 60,
                "addresses": {
                    "public": [{
                        "version": 4,
                        "addr": "1.2.3.4",
                    },
                    {
                        "version": 4,
                        "addr": "5.6.7.8",
                    }],
                    "private": [{
                        "version": 4,
                        "addr": "10.11.12.13",
                    }],
                },
                "metadata": {
                    "Server Label": "Web Head 1",
                    "Image Version": "2.1"
                }
            },
            {
                "id": 5678,
                "name": "sample-server2",
                "image": {
                    "id": 2,
                    "name": "sample image",
                },
                "flavor": {
                    "id": 1,
                    "name": "256 MB Server",
                },
                "hostId": "9e107d9d372bb6826bd81d3542a419d6",
                "status": "ACTIVE",
                "addresses": {
                    "public": [{
                        "version": 4,
                        "addr": "4.5.6.7",
                    },
                    {
                        "version": 4,
                        "addr": "5.6.9.8",
                    }],
                    "private": [{
                        "version": 4,
                        "addr": "10.13.12.13",
                    }],
                },
                "metadata": {
                    "Server Label": "DB 1"
                }
            },
            {
                "id": 9012,
                "name": "sample-server3",
                "image": "",
                "flavor": {
                    "id": 1,
                    "name": "256 MB Server",
                },
                "hostId": "9e107d9d372bb6826bd81d3542a419d6",
                "status": "ACTIVE",
                "addresses": {
                    "public": [{
                        "version": 4,
                        "addr": "4.5.6.7",
                    },
                    {
                        "version": 4,
                        "addr": "5.6.9.8",
                    }],
                    "private": [{
                        "version": 4,
                        "addr": "10.13.12.13",
                    }],
                },
                "metadata": {
                    "Server Label": "DB 1"
                }
            }
        ]})

    def post_servers(self, body, **kw):
        assert set(body.keys()) <= set(['server', 'os:scheduler_hints'])
        fakes.assert_has_keys(body['server'],
                        required=['name', 'imageRef', 'flavorRef'],
                        optional=['metadata', 'personality'])
        if 'personality' in body['server']:
            for pfile in body['server']['personality']:
                fakes.assert_has_keys(pfile, required=['path', 'contents'])
        return (202, self.get_servers_1234()[1])

    def post_os_volumes_boot(self, body, **kw):
        assert set(body.keys()) <= set(['server', 'os:scheduler_hints'])
        fakes.assert_has_keys(body['server'],
                        required=['name', 'block_device_mapping', 'flavorRef'],
                        optional=['imageRef'])
        return (202, self.get_servers_9012()[1])

    def get_servers_1234(self, **kw):
        r = {'server': self.get_servers_detail()[1]['servers'][0]}
        return (200, r)

    def get_servers_5678(self, **kw):
        r = {'server': self.get_servers_detail()[1]['servers'][1]}
        return (200, r)

    def get_servers_9012(self, **kw):
        r = {'server': self.get_servers_detail()[1]['servers'][2]}
        return (200, r)

    def put_servers_1234(self, body, **kw):
        assert body.keys() == ['server']
        fakes.assert_has_keys(body['server'], optional=['name', 'adminPass'])
        return (204, None)

    def delete_servers_1234(self, **kw):
        return (202, None)

    def delete_servers_1234_metadata_test_key(self, **kw):
        return (204, None)

    def delete_servers_1234_metadata_key1(self, **kw):
        return (204, None)

    def delete_servers_1234_metadata_key2(self, **kw):
        return (204, None)

    def post_servers_1234_metadata(self, **kw):
        return (204, {'metadata': {'test_key': 'test_value'}})

    def get_servers_1234_diagnostics(self, **kw):
        return (200, {'data': 'Fake diagnostics'})

    def get_servers_1234_actions(self, **kw):
        return (200, {'actions': [
            {
                'action': 'rebuild',
                'error': None,
                'created_at': '2011-12-30 11:45:36'
            },
            {
                'action': 'reboot',
                'error': 'Failed!',
                'created_at': '2011-12-30 11:40:29'
            },
        ]})

    #
    # Server Addresses
    #

    def get_servers_1234_ips(self, **kw):
        return (200, {'addresses':
                      self.get_servers_1234()[1]['server']['addresses']})

    def get_servers_1234_ips_public(self, **kw):
        return (200, {'public':
                      self.get_servers_1234_ips()[1]['addresses']['public']})

    def get_servers_1234_ips_private(self, **kw):
        return (200, {'private':
                      self.get_servers_1234_ips()[1]['addresses']['private']})

    def delete_servers_1234_ips_public_1_2_3_4(self, **kw):
        return (202, None)

    #
    # Server actions
    #

    def post_servers_1234_action(self, body, **kw):
        _body = None
        resp = 202
        assert len(body.keys()) == 1
        action = body.keys()[0]
        if action == 'reboot':
            assert body[action].keys() == ['type']
            assert body[action]['type'] in ['HARD', 'SOFT']
        elif action == 'rebuild':
            keys = body[action].keys()
            if 'adminPass' in keys:
                keys.remove('adminPass')
            assert keys == ['imageRef']
            _body = self.get_servers_1234()[1]
        elif action == 'resize':
            assert body[action].keys() == ['flavorRef']
        elif action == 'confirmResize':
            assert body[action] is None
            # This one method returns a different response code
            return (204, None)
        elif action == 'revertResize':
            assert body[action] is None
        elif action == 'migrate':
            assert body[action] is None
        elif action == 'os-stop':
            assert body[action] is None
        elif action == 'os-start':
            assert body[action] is None
        elif action == 'rescue':
            assert body[action] is None
        elif action == 'unrescue':
            assert body[action] is None
        elif action == 'lock':
            assert body[action] is None
        elif action == 'unlock':
            assert body[action] is None
        elif action == 'addFixedIp':
            assert body[action].keys() == ['networkId']
        elif action == 'removeFixedIp':
            assert body[action].keys() == ['address']
        elif action == 'addFloatingIp':
            assert body[action].keys() == ['address']
        elif action == 'removeFloatingIp':
            assert body[action].keys() == ['address']
        elif action == 'createImage':
            assert set(body[action].keys()) == set(['name', 'metadata'])
            resp = dict(status=202, location="http://blah/images/456")
        elif action == 'changePassword':
            assert body[action].keys() == ['adminPass']
        elif action == 'os-getConsoleOutput':
            assert body[action].keys() == ['length']
            return (202, {'output': 'foo'})
        elif action == 'os-getVNCConsole':
            assert body[action].keys() == ['type']
        elif action == 'os-migrateLive':
            assert set(body[action].keys()) == set(['host',
                                                    'block_migration',
                                                    'disk_over_commit'])
        elif action == 'os-resetState':
            assert body[action].keys() == ['state']
        elif action == 'addSecurityGroup':
            assert body[action].keys() == ['name']
        elif action == 'removeSecurityGroup':
            assert body[action].keys() == ['name']
        elif action == 'createBackup':
            assert set(body[action].keys()) == set(['name',
                                                    'backup_type',
                                                    'rotation'])
        else:
            raise AssertionError("Unexpected server action: %s" % action)
        return (resp, _body)

    #
    # Cloudpipe
    #

    def get_os_cloudpipe(self, **kw):
        return (200, {'cloudpipes': [
            {'project_id':1}
        ]})

    def post_os_cloudpipe(self, **ks):
        return (202, {'instance_id': '9d5824aa-20e6-4b9f-b967-76a699fc51fd'})

    def put_os_cloudpipe_configure_project(self, **kw):
        return (202, None)

    #
    # Flavors
    #

    def get_flavors(self, **kw):
        return (200, {'flavors': [
            {'id': 1, 'name': '256 MB Server'},
            {'id': 2, 'name': '512 MB Server'},
            {'id': 'aa1', 'name': '128 MB Server'}
        ]})

    def get_flavors_detail(self, **kw):
        return (200, {'flavors': [
            {'id': 1, 'name': '256 MB Server', 'ram': 256, 'disk': 10,
             'OS-FLV-EXT-DATA:ephemeral': 10,
             'os-flavor-access:is_public': True,
             'links': {}},
            {'id': 2, 'name': '512 MB Server', 'ram': 512, 'disk': 20,
             'OS-FLV-EXT-DATA:ephemeral': 20,
             'os-flavor-access:is_public': False,
             'links': {}},
            {'id': 'aa1', 'name': '128 MB Server', 'ram': 128, 'disk': 0,
             'OS-FLV-EXT-DATA:ephemeral': 0,
             'os-flavor-access:is_public': True,
             'links': {}}
        ]})

    def get_flavors_1(self, **kw):
        return (200, {'flavor': self.get_flavors_detail()[1]['flavors'][0]})

    def get_flavors_2(self, **kw):
        return (200, {'flavor': self.get_flavors_detail()[1]['flavors'][1]})

    def get_flavors_3(self, **kw):
        # Diablo has no ephemeral
        return (200, {'flavor': {'id': 3, 'name': '256 MB Server',
                                 'ram': 256, 'disk': 10}})

    def get_flavors_aa1(self, **kw):
        # Aplhanumeric flavor id are allowed.
        return (200, {'flavor': self.get_flavors_detail()[1]['flavors'][2]})

    def delete_flavors_flavordelete(self, **kw):
        return (202, None)

    def post_flavors(self, body, **kw):
        return (202, {'flavor': self.get_flavors_detail()[1]['flavors'][0]})

    def get_flavors_1_os_extra_specs(self, **kw):
        return (200,
            {'extra_specs': {"k1": "v1"}})

    def get_flavors_2_os_extra_specs(self, **kw):
        return (200,
            {'extra_specs': {"k2": "v2"}})

    def get_flavors_aa1_os_extra_specs(self, **kw):
        return (200,
            {'extra_specs': {"k3": "v3"}})

    def post_flavors_1_os_extra_specs(self, body, **kw):
        assert body.keys() == ['extra_specs']
        fakes.assert_has_keys(body['extra_specs'],
                              required=['k1'])
        return (200,
            {'extra_specs': {"k1": "v1"}})

    def delete_flavors_1_os_extra_specs_k1(self, **kw):
        return (204, None)

    #
    # Flavor access
    #

    def get_flavors_1_os_flavor_access(self, **kw):
        return (404, None)

    def get_flavors_2_os_flavor_access(self, **kw):
        return (200, {'flavor_access': [
            {'flavor_id': '2', 'tenant_id': 'proj1'},
            {'flavor_id': '2', 'tenant_id': 'proj2'}
        ]})

    def post_flavors_2_action(self, body, **kw):
        return (202, self.get_flavors_2_os_flavor_access()[1])

    #
    # Floating ips
    #

    def get_os_floating_ip_pools(self):
        return (200, {'floating_ip_pools': [{'name': 'foo', 'name': 'bar'}]})

    def get_os_floating_ips(self, **kw):
        return (200, {'floating_ips': [
            {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1'},
            {'id': 2, 'fixed_ip': '10.0.0.2', 'ip': '11.0.0.2'},
        ]})

    def get_os_floating_ips_1(self, **kw):
        return (200, {'floating_ip':
            {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1'}
        })

    def post_os_floating_ips(self, body, **kw):
        return (202, self.get_os_floating_ips_1()[1])

    def post_os_floating_ips(self, body):
        if body.get('pool'):
            return (200, {'floating_ip':
                {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1',
                                                            'pool': 'nova'}})
        else:
            return (200, {'floating_ip':
                {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1',
                                                            'pool': None}})

    def delete_os_floating_ips_1(self, **kw):
        return (204, None)

    def get_os_floating_ip_dns(self, **kw):
        return (205, {'domain_entries':
                      [{'domain': 'example.org'},
                       {'domain': 'example.com'}]})

    def get_os_floating_ip_dns_testdomain_entries(self, **kw):
        if kw.get('ip'):
            return (205, {'dns_entries':
                          [{'dns_entry':
                             {'ip': kw.get('ip'),
                              'name': "host1",
                              'type': "A",
                              'domain': 'testdomain'}},
                           {'dns_entry':
                             {'ip': kw.get('ip'),
                              'name': "host2",
                              'type': "A",
                              'domain': 'testdomain'}}]})
        else:
            return (404, None)

    def get_os_floating_ip_dns_testdomain_entries_testname(self, **kw):
        return (205, {'dns_entry':
                        {'ip': "10.10.10.10",
                         'name': 'testname',
                         'type': "A",
                         'domain': 'testdomain'}})

    def put_os_floating_ip_dns_testdomain(self, body, **kw):
        if body['domain_entry']['scope'] == 'private':
            fakes.assert_has_keys(body['domain_entry'],
                            required=['availability_zone', 'scope'])
        elif body['domain_entry']['scope'] == 'public':
            fakes.assert_has_keys(body['domain_entry'],
                            required=['project', 'scope'])

        else:
            fakes.assert_has_keys(body['domain_entry'],
                            required=['project', 'scope'])
        return (205, None)

    def put_os_floating_ip_dns_testdomain_entries_testname(self, body, **kw):
        fakes.assert_has_keys(body['dns_entry'],
                        required=['ip', 'dns_type'])
        return (205, None)

    def delete_os_floating_ip_dns_testdomain(self, **kw):
        return (200, None)

    def delete_os_floating_ip_dns_testdomain_entries_testname(self, **kw):
        return (200, None)

    def get_os_floating_ips_bulk(self, **kw):
        return (200, {'floating_ip_info': [
            {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1'},
            {'id': 2, 'fixed_ip': '10.0.0.2', 'ip': '11.0.0.2'},
        ]})

    def get_os_floating_ips_bulk_testHost(self, **kw):
        return (200, {'floating_ip_info': [
            {'id': 1, 'fixed_ip': '10.0.0.1', 'ip': '11.0.0.1'},
            {'id': 2, 'fixed_ip': '10.0.0.2', 'ip': '11.0.0.2'},
        ]})

    def post_os_floating_ips_bulk(self, **kw):
        params = kw.get('body').get('floating_ips_bulk_create')
        pool = params.get('pool', 'defaultPool')
        interface = params.get('interface', 'defaultInterface')
        return (200, {'floating_ips_bulk_create':
                          {'ip_range': '192.168.1.0/30',
                           'pool': pool,
                           'interface': interface}})

    def put_os_floating_ips_bulk_delete(self, **kw):
        ip_range = kw.get('body').get('ip_range')
        return (200, {'floating_ips_bulk_delete': ip_range})

    #
    # Images
    #
    def get_images(self, **kw):
        return (200, {'images': [
            {'id': 1, 'name': 'CentOS 5.2'},
            {'id': 2, 'name': 'My Server Backup'}
        ]})

    def get_images_detail(self, **kw):
        return (200, {'images': [
            {
                'id': 1,
                'name': 'CentOS 5.2',
                "updated": "2010-10-10T12:00:00Z",
                "created": "2010-08-10T12:00:00Z",
                "status": "ACTIVE",
                "metadata": {
                    "test_key": "test_value",
                },
                "links": {},
            },
            {
                "id": 743,
                "name": "My Server Backup",
                "serverId": 1234,
                "updated": "2010-10-10T12:00:00Z",
                "created": "2010-08-10T12:00:00Z",
                "status": "SAVING",
                "progress": 80,
                "links": {},
            }
        ]})

    def get_images_1(self, **kw):
        return (200, {'image': self.get_images_detail()[1]['images'][0]})

    def get_images_2(self, **kw):
        return (200, {'image': self.get_images_detail()[1]['images'][1]})

    def post_images(self, body, **kw):
        assert body.keys() == ['image']
        fakes.assert_has_keys(body['image'], required=['serverId', 'name'])
        return (202, self.get_images_1()[1])

    def post_images_1_metadata(self, body, **kw):
        assert body.keys() == ['metadata']
        fakes.assert_has_keys(body['metadata'],
                              required=['test_key'])
        return (200,
            {'metadata': self.get_images_1()[1]['image']['metadata']})

    def delete_images_1(self, **kw):
        return (204, None)

    def delete_images_1_metadata_test_key(self, **kw):
        return (204, None)

    #
    # Keypairs
    #
    def get_os_keypairs(self, *kw):
        return (200, {"keypairs": [
            {'fingerprint': 'FAKE_KEYPAIR', 'name': 'test'}
        ]})

    def delete_os_keypairs_test(self, **kw):
        return (202, None)

    def post_os_keypairs(self, body, **kw):
        assert body.keys() == ['keypair']
        fakes.assert_has_keys(body['keypair'],
                              required=['name'])
        r = {'keypair': self.get_os_keypairs()[1]['keypairs'][0]}
        return (202, r)

    #
    # Virtual Interfaces
    #
    def get_servers_1234_os_virtual_interfaces(self, **kw):
        return (200, {"virtual_interfaces": [
            {'id': 'fakeid', 'mac_address': 'fakemac'}
        ]})

    #
    # Quotas
    #

    def get_os_quota_sets_test(self, **kw):
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'injected_file_content_bytes': 1,
                      'injected_file_path_bytes': 1,
                      'volumes': 1,
                      'gigabytes': 1,
                      'ram': 1,
                      'floating_ips': 1,
                      'instances': 1,
                      'injected_files': 1,
                      'cores': 1,
                      'keypairs': 1,
                      'security_groups': 1,
                      'security_group_rules': 1}})

    def get_os_quota_sets_test_defaults(self):
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'injected_file_content_bytes': 1,
                      'injected_file_path_bytes': 1,
                      'volumes': 1,
                      'gigabytes': 1,
                      'ram': 1,
                      'floating_ips': 1,
                      'instances': 1,
                      'injected_files': 1,
                      'cores': 1,
                      'keypairs': 1,
                      'security_groups': 1,
                      'security_group_rules': 1}})

    def put_os_quota_sets_test(self, body, **kw):
        assert body.keys() == ['quota_set']
        fakes.assert_has_keys(body['quota_set'],
                              required=['tenant_id'])
        return (200, {'quota_set': {
                      'tenant_id': 'test',
                      'metadata_items': [],
                      'injected_file_content_bytes': 1,
                      'injected_file_path_bytes': 1,
                      'volumes': 2,
                      'gigabytes': 1,
                      'ram': 1,
                      'floating_ips': 1,
                      'instances': 1,
                      'injected_files': 1,
                      'cores': 1,
                      'keypairs': 1,
                      'security_groups': 1,
                      'security_group_rules': 1}})

    #
    # Quota Classes
    #

    def get_os_quota_class_sets_test(self, **kw):
        return (200, {'quota_class_set': {
                      'class_name': 'test',
                      'metadata_items': [],
                      'injected_file_content_bytes': 1,
                      'injected_file_path_bytes': 1,
                      'volumes': 1,
                      'gigabytes': 1,
                      'ram': 1,
                      'floating_ips': 1,
                      'instances': 1,
                      'injected_files': 1,
                      'cores': 1,
                      'keypairs': 1,
                      'security_groups': 1,
                      'security_group_rules': 1}})

    def put_os_quota_class_sets_test(self, body, **kw):
        assert body.keys() == ['quota_class_set']
        fakes.assert_has_keys(body['quota_class_set'],
                              required=['class_name'])
        return (200, {'quota_class_set': {
                      'class_name': 'test',
                      'metadata_items': [],
                      'injected_file_content_bytes': 1,
                      'injected_file_path_bytes': 1,
                      'volumes': 2,
                      'gigabytes': 1,
                      'ram': 1,
                      'floating_ips': 1,
                      'instances': 1,
                      'injected_files': 1,
                      'cores': 1,
                      'keypairs': 1,
                      'security_groups': 1,
                      'security_group_rules': 1}})

    #
    # Security Groups
    #
    def get_os_security_groups(self, **kw):
        return (200, {"security_groups": [
                {'id': 1, 'name': 'test', 'description': 'FAKE_SECURITY_GROUP',
                 'tenant_id': '4ffc664c198e435e9853f2538fbcd7a7'}
        ]})

    def get_os_security_groups_1(self, **kw):
        return (200, {"security_group":
                {'id': 1, 'name': 'test', 'description': 'FAKE_SECURITY_GROUP'}
        })

    def delete_os_security_groups_1(self, **kw):
        return (202, None)

    def post_os_security_groups(self, body, **kw):
        assert body.keys() == ['security_group']
        fakes.assert_has_keys(body['security_group'],
                              required=['name', 'description'])
        r = {'security_group':
                self.get_os_security_groups()[1]['security_groups'][0]}
        return (202, r)

    #
    # Security Group Rules
    #
    def get_os_security_group_rules(self, **kw):
        return (200, {"security_group_rules": [
                {'id': 1, 'parent_group_id': 1, 'group_id': 2,
                 'ip_protocol': 'TCP', 'from_port': '22', 'to_port': 22,
                 'cidr': '10.0.0.0/8'}
        ]})

    def delete_os_security_group_rules_1(self, **kw):
        return (202, None)

    def post_os_security_group_rules(self, body, **kw):
        assert body.keys() == ['security_group_rule']
        fakes.assert_has_keys(body['security_group_rule'],
            required=['parent_group_id'],
            optional=['group_id', 'ip_protocol', 'from_port',
                      'to_port', 'cidr'])
        r = {'security_group_rule':
            self.get_os_security_group_rules()[1]['security_group_rules'][0]}
        return (202, r)

    #
    # Tenant Usage
    #
    def get_os_simple_tenant_usage(self, **kw):
        return (200, {u'tenant_usages': [{
            u'total_memory_mb_usage': 25451.762807466665,
            u'total_vcpus_usage': 49.71047423333333,
            u'total_hours': 49.71047423333333,
            u'tenant_id': u'7b0a1d73f8fb41718f3343c207597869',
            u'stop': u'2012-01-22 19:48:41.750722',
            u'server_usages': [{
                u'hours': 49.71047423333333,
                u'uptime': 27035, u'local_gb': 0, u'ended_at': None,
                u'name': u'f15image1',
                u'tenant_id': u'7b0a1d73f8fb41718f3343c207597869',
                u'vcpus': 1, u'memory_mb': 512, u'state': u'active',
                u'flavor': u'm1.tiny',
                u'started_at': u'2012-01-20 18:06:06.479998'}],
            u'start': u'2011-12-25 19:48:41.750687',
            u'total_local_gb_usage': 0.0}]})

    def get_os_simple_tenant_usage_tenantfoo(self, **kw):
        return (200, {u'tenant_usage': {
            u'total_memory_mb_usage': 25451.762807466665,
            u'total_vcpus_usage': 49.71047423333333,
            u'total_hours': 49.71047423333333,
            u'tenant_id': u'7b0a1d73f8fb41718f3343c207597869',
            u'stop': u'2012-01-22 19:48:41.750722',
            u'server_usages': [{
                u'hours': 49.71047423333333,
                u'uptime': 27035, u'local_gb': 0, u'ended_at': None,
                u'name': u'f15image1',
                u'tenant_id': u'7b0a1d73f8fb41718f3343c207597869',
                u'vcpus': 1, u'memory_mb': 512, u'state': u'active',
                u'flavor': u'm1.tiny',
                u'started_at': u'2012-01-20 18:06:06.479998'}],
            u'start': u'2011-12-25 19:48:41.750687',
            u'total_local_gb_usage': 0.0}})

    #
    # Certificates
    #
    def get_os_certificates_root(self, **kw):
        return (200, {'certificate': {'private_key': None, 'data': 'foo'}})

    def post_os_certificates(self, **kw):
        return (200, {'certificate': {'private_key': 'foo', 'data': 'bar'}})

    #
    # Aggregates
    #
    def get_os_aggregates(self, *kw):
        return (200, {"aggregates": [
            {'id':'1',
             'name': 'test',
             'availability_zone': 'nova1'},
            {'id':'2',
             'name': 'test2',
             'availability_zone': 'nova1'},
        ]})

    def _return_aggregate(self):
        r = {'aggregate': self.get_os_aggregates()[1]['aggregates'][0]}
        return (200, r)

    def get_os_aggregates_1(self, **kw):
        return self._return_aggregate()

    def post_os_aggregates(self, body, **kw):
        return self._return_aggregate()

    def put_os_aggregates_1(self, body, **kw):
        return self._return_aggregate()

    def put_os_aggregates_2(self, body, **kw):
        return self._return_aggregate()

    def post_os_aggregates_1_action(self, body, **kw):
        return self._return_aggregate()

    def post_os_aggregates_2_action(self, body, **kw):
        return self._return_aggregate()

    def delete_os_aggregates_1(self, **kw):
        return (202, None)

    #
    # Services
    #
    def get_os_services(self, **kw):
        host = kw.get('host', 'host1')
        service = kw.get('service', 'nova-compute')
        return (200, {'services':
                     [{'binary': service,
                       'host': host,
                       'zone': 'nova',
                       'status': 'enabled',
                       'state': 'up',
                       'updated_at': datetime(2012, 10, 29, 13, 42, 2)},
                      {'binary': service,
                       'host': host,
                       'zone': 'nova',
                       'status': 'disabled',
                       'state': 'down',
                       'updated_at': datetime(2012, 9, 18, 8, 3, 38)},
                      ]})

    def put_os_services_enable(self, body, **kw):
        return (200, {'host': body['host'], 'service': body['service'],
                'disabled': False})

    def put_os_services_disable(self, body, **kw):
        return (200, {'host': body['host'], 'service': body['service'],
                'disabled': True})

    #
    # Fixed IPs
    #
    def get_os_fixed_ips_192_168_1_1(self, *kw):
        return (200, {"fixed_ip":
                      {'cidr': '192.168.1.0/24',
                       'address': '192.168.1.1',
                       'hostname': 'foo',
                       'host': 'bar'}})

    def post_os_fixed_ips_192_168_1_1_action(self, body, **kw):
        return (202, None)

    #
    # Hosts
    #
    def get_os_hosts_host(self, *kw):
        return (200, {'host':
                [{'resource': {'project': '(total)', 'host': 'dummy',
                  'cpu': 16, 'memory_mb': 32234, 'disk_gb': 128}},
                 {'resource': {'project': '(used_now)', 'host': 'dummy',
                  'cpu': 1, 'memory_mb': 2075, 'disk_gb': 45}},
                 {'resource': {'project': '(used_max)', 'host': 'dummy',
                  'cpu': 1, 'memory_mb': 2048, 'disk_gb': 30}},
                 {'resource': {'project': 'admin', 'host': 'dummy',
                  'cpu': 1, 'memory_mb': 2048, 'disk_gb': 30}}]})

    def get_os_hosts(self, **kw):
        zone = kw.get('zone', 'nova1')
        return (200, {'hosts':
                    [{'host': 'host1',
                      'service': 'nova-compute',
                      'zone': zone},
                     {'host': 'host1',
                      'service': 'nova-cert',
                      'zone': zone}]})

    def get_os_hosts_sample_host(self, *kw):
        return (200, {'host': [{'resource': {'host': 'sample_host'}}], })

    def put_os_hosts_sample_host_1(self, body, **kw):
        return (200, {'host': 'sample-host_1',
                      'status': 'enabled'})

    def put_os_hosts_sample_host_2(self, body, **kw):
        return (200, {'host': 'sample-host_2',
                      'maintenance_mode': 'on_maintenance'})

    def put_os_hosts_sample_host_3(self, body, **kw):
        return (200, {'host': 'sample-host_3',
                      'status': 'enabled',
                      'maintenance_mode': 'on_maintenance'})

    def get_os_hosts_sample_host_startup(self, **kw):
        return (200, {'host': 'sample_host',
                      'power_action': 'startup'})

    def get_os_hosts_sample_host_reboot(self, **kw):
        return (200, {'host': 'sample_host',
                      'power_action': 'reboot'})

    def get_os_hosts_sample_host_shutdown(self, **kw):
        return (200, {'host': 'sample_host',
                      'power_action': 'shutdown'})

    def put_os_hosts_sample_host(self, body, **kw):
        result = {'host': 'dummy'}
        result.update(body)
        return (200, result)

    def get_os_hypervisors(self, **kw):
        return (200, {"hypervisors": [
                    {'id': 1234, 'hypervisor_hostname': 'hyper1'},
                    {'id': 5678, 'hypervisor_hostname': 'hyper2'},
                    ]})

    def get_os_hypervisors_detail(self, **kw):
        return (200, {"hypervisors": [
                    {'id': 1234,
                     'service': {'id': 1, 'host': 'compute1'},
                     'vcpus': 4,
                     'memory_mb': 10 * 1024,
                     'local_gb': 250,
                     'vcpus_used': 2,
                     'memory_mb_used': 5 * 1024,
                     'local_gb_used': 125,
                     'hypervisor_type': "xen",
                     'hypervisor_version': 3,
                     'hypervisor_hostname': "hyper1",
                     'free_ram_mb': 5 * 1024,
                     'free_disk_gb': 125,
                     'current_workload': 2,
                     'running_vms': 2,
                     'cpu_info': 'cpu_info',
                     'disk_available_least': 100},
                    {'id': 2,
                     'service': {'id': 2, 'host': "compute2"},
                     'vcpus': 4,
                     'memory_mb': 10 * 1024,
                     'local_gb': 250,
                     'vcpus_used': 2,
                     'memory_mb_used': 5 * 1024,
                     'local_gb_used': 125,
                     'hypervisor_type': "xen",
                     'hypervisor_version': 3,
                     'hypervisor_hostname': "hyper2",
                     'free_ram_mb': 5 * 1024,
                     'free_disk_gb': 125,
                     'current_workload': 2,
                     'running_vms': 2,
                     'cpu_info': 'cpu_info',
                     'disk_available_least': 100}
                    ]})

    def get_os_hypervisors_statistics(self, **kw):
        return (200, {"hypervisor_statistics": {
                    'count': 2,
                    'vcpus': 8,
                    'memory_mb': 20 * 1024,
                    'local_gb': 500,
                    'vcpus_used': 4,
                    'memory_mb_used': 10 * 1024,
                    'local_gb_used': 250,
                    'free_ram_mb': 10 * 1024,
                    'free_disk_gb': 250,
                    'current_workload': 4,
                    'running_vms': 4,
                    'disk_available_least': 200,
                    }})

    def get_os_hypervisors_hyper_search(self, **kw):
        return (200, {'hypervisors': [
                    {'id': 1234, 'hypervisor_hostname': 'hyper1'},
                    {'id': 5678, 'hypervisor_hostname': 'hyper2'}
                    ]})

    def get_os_hypervisors_hyper_servers(self, **kw):
        return (200, {'hypervisors': [
                    {'id': 1234,
                     'hypervisor_hostname': 'hyper1',
                     'servers': [
                            {'name': 'inst1', 'uuid': 'uuid1'},
                            {'name': 'inst2', 'uuid': 'uuid2'}
                            ]},
                    {'id': 5678,
                     'hypervisor_hostname': 'hyper2',
                     'servers': [
                            {'name': 'inst3', 'uuid': 'uuid3'},
                            {'name': 'inst4', 'uuid': 'uuid4'}
                            ]}
                    ]})

    def get_os_hypervisors_1234(self, **kw):
        return (200, {'hypervisor':
                          {'id': 1234,
                           'service': {'id': 1, 'host': 'compute1'},
                           'vcpus': 4,
                           'memory_mb': 10 * 1024,
                           'local_gb': 250,
                           'vcpus_used': 2,
                           'memory_mb_used': 5 * 1024,
                           'local_gb_used': 125,
                           'hypervisor_type': "xen",
                           'hypervisor_version': 3,
                           'hypervisor_hostname': "hyper1",
                           'free_ram_mb': 5 * 1024,
                           'free_disk_gb': 125,
                           'current_workload': 2,
                           'running_vms': 2,
                           'cpu_info': 'cpu_info',
                           'disk_available_least': 100}})

    def get_os_hypervisors_1234_uptime(self, **kw):
        return (200, {'hypervisor':
                          {'id': 1234,
                           'hypervisor_hostname': "hyper1",
                           'uptime': "fake uptime"}})

    def get_os_networks(self, **kw):
        return (200, {'networks': [{"label": "1", "cidr": "10.0.0.0/24",
                'project_id': '4ffc664c198e435e9853f2538fbcd7a7',
                'id': '1'}]})

    def get_os_networks_1(self, **kw):
        return (200, {'network': {"label": "1", "cidr": "10.0.0.0/24"}})

    def post_os_networks(self, **kw):
        return (202, {'network': kw})

    def post_os_networks_1_action(self, **kw):
        return (202, None)

    def delete_os_networks_networkdelete(self, **kw):
        return (202, None)

    def post_os_networks_add(self, **kw):
        return (202, None)

    def post_os_networks_networkdisassociate_action(self, **kw):
        return (202, None)

    def get_os_fping(self, **kw):
        return (
            200, {
                'servers': [
                    {
                        "id": "1",
                        "project_id": "fake-project",
                        "alive": True,
                    },
                    {
                        "id": "2",
                        "project_id": "fake-project",
                        "alive": True,
                    },
                ]
            }
        )

    def get_os_fping_1(self, **kw):
        return (
            200, {
                'server': {
                    "id": "1",
                    "project_id": "fake-project",
                    "alive": True,
                }
            }
        )

    def post_os_networks(self, **kw):
        return (202, {'network': kw})

    def post_os_networks_1_action(self, **kw):
        return (202, None)

    def post_os_networks_networktest_action(self, **kw):
        return (202, None)

    def post_os_networks_2_action(self, **kw):
        return (202, None)
