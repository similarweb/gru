import re
from collections import Counter

import boto3
import botocore.exceptions

from gru.config import settings
from gru.plugins.base.inventory import InventoryProvider, Host, HostCategory, HostList


DEFAULT_AWS_REGION = 'us-east-1'


class RegionConnection(object):

    def __init__(self, region, connection):
        self.region = region
        self.connection = connection


class EC2Provider(InventoryProvider):

    required_settings = [
        'inventory.config.accounts'
    ]

    def __init__(self, *args, **kwargs):
        super(EC2Provider, self).__init__(*args, **kwargs)
        self.conns = []

    def on_load(self):
        for conn in settings.get('inventory.config.accounts'):
            boto_kwargs = {}
            if 'aws_access_key_id' in conn:
                boto_kwargs['aws_access_key_id'] = conn.get('aws_access_key_id')
            if 'aws_secret_access_key' in conn:
                boto_kwargs['aws_secret_access_key'] = conn.get('aws_secret_access_key')
            regions = conn.get('regions', [])
            if not regions:
                self.conns.append(RegionConnection(DEFAULT_AWS_REGION, boto3.resource('ec2', **boto_kwargs)))
                continue
            for region in regions:
                region_kwargs = boto_kwargs.copy()
                region_kwargs['region_name'] = region
                self.conns.append(RegionConnection(region, boto3.resource('ec2', **region_kwargs)))

    def host_group_breakdown(self, category):
        group_counter = Counter()
        for conn in self.conns:
            for instance in conn.connection.instances.all():
                host = self._host_from_instance(instance)
                if host.field(category) is not None:
                    group_counter[host.field(category)] += 1
        groups = []
        for k, v in group_counter.most_common():
            groups.append(HostCategory(category=category, group=k, count=v))
        return groups

    @staticmethod
    def _host_from_instance(instance):
        host_data = {
            'instance-type': instance.instance_type,
            'image-id': instance.image_id,
            'architecture': instance.architecture,
            'hypervisor': instance.hypervisor,
            'key_pair': instance.key_name,
            'launch-time': str(instance.launch_time),
            'availability-zone': instance.placement.get('AvailabilityZone'),
            'region': instance.placement.get('AvailabilityZone', '')[:-1],
            'private-dns-name': instance.private_dns_name,
            'private-ip-address': instance.private_ip_address,
            'dns-name': instance.public_dns_name,
            'ip-address': instance.public_ip_address,
            'root_device_type': instance.root_device_type,
            'root_device_name': instance.root_device_name,
            'instance.group-id': ', '.join([sg.get('GroupName') for sg in instance.security_groups]),
            'instance.group-name': ', '.join([sg.get('GroupId') for sg in instance.security_groups]),
            'source-dest-check': instance.source_dest_check,
            'spot-instance-request-id': instance.spot_instance_request_id,
            'instance-lifecycle': 'spot' if instance.spot_instance_request_id is not None else 'scheduled',
            'instance-state-name': instance.state.get('Name'),
            'subnet-id': instance.subnet_id,
            'vpc-id': instance.vpc_id,
            'virtualization-type': instance.virtualization_type,
        }
        if instance.tags:
            host_data.update({'tag:{}'.format(tag.get('Key')): tag.get('Value') for tag in instance.tags})
        return Host(
            host_id=instance.instance_id,
            host_data=host_data)

    def list(self, category, group, sort_by=None, from_ind=None, to_ind=None):
        hosts = []
        if category == 'region':
            conn = filter(lambda c: c.region == group, self.conns)
            if len(conn) == 1:
                hosts += [self._host_from_instance(instance) for instance in conn[0].connection.instances.all()]
        else:
            for conn in self.conns:
                instances = conn.connection.instances.filter(Filters=[{'Name': category, 'Values': [group]}]).all()
                hosts += [self._host_from_instance(instance) for instance in instances.all()]
        return HostList(total_hosts=len(hosts), hosts=hosts)

    def host_search(self, query, from_ind=None, to_ind=None):
        m = re.match(r'(?P<key>.*?)[\s\t]*\=[\s\t]*[\'\"]?(?P<value>[^\'\"]*)[\'\"]?', query)
        if not m:
            return HostList()
        filters = [{'Name': m.group('key'), 'Values': [m.group('value')]}]
        hosts = []
        for conn in self.conns:
            try:
                instances = conn.connection.instances.filter(Filters=filters).all()
                hosts += [self._host_from_instance(instance) for instance in instances.all()]
            except botocore.exceptions.ClientError:
                continue  # Most likely an invalid filter
        return HostList(total_hosts=len(hosts), hosts=hosts)

    def get_host_by_id(self, host_id):
        filters = [{'Name': 'instance-id', 'Values': [host_id]}]
        for conn in self.conns:
            instances = list(conn.connection.instances.filter(Filters=filters).all())
            if len(instances) == 1:
                return self._host_from_instance(instances[0])
        return None
