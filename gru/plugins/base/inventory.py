
from . import BasePlugin

from gru.config import settings


class Host(object):

    def __init__(self, host_id, host_data=None):
        self.host_id = host_id
        if host_data:
            self.host_data = host_data
        else:
            self.host_data = {}

    def __repr__(self):
        return 'Host(host_id="{}")'.format(
            self.host_id,
            self.host_data
        )

    def __str__(self):
        return self.__repr__()

    def get_identifier(self):
        return self.host_id

    def get_display_name(self):
        display_name = self.field(settings.get('inventory.host_display_name_field'), None)
        if not display_name:
            display_name = self.host_id
        return display_name

    def field(self, field_name, default=None):
        """
        Return a (possibly nested) field
        :param field_name: the name of the field to return. If it contains periods ("."), a nested lookup will be
            performed
        :param default: a default value to return if the field is not found
        :return: The value matching the field name inside the host data
        """
        try:
            return self.host_data[field_name]
        except KeyError:
            pass
        parts = field_name.split('.')
        current_val = self.host_data
        for part in parts:
            try:
                current_val = current_val[part]
            except (KeyError, TypeError):
                return default
            except TypeError:
                return default
        return current_val


class HostCategory(object):

    def __init__(self, category, group, count=0):
        self.category = category
        self.group = group
        self.count = count

    def __repr__(self):
        return 'HostCategory(category="{}", group="{}", count={})'.format(
            self.category,
            self.group,
            self.count
        )

    def __str__(self):
        return self.__repr__()


class HostList(object):

    def __init__(self, hosts=None, total_hosts=0):
        if hosts:
            self.hosts = hosts
        else:
            self.hosts = []
        self.total_hosts = total_hosts

    def __repr__(self):
        return 'HostList(hosts={}..., total_hosts={})'.format(
            self.hosts[:5],
            self.total_hosts
        )

    def append(self, host):
        self.hosts.append(host)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for host in self.hosts:
            yield host

    def __nonzero__(self):
        return self.hosts.__nonzero__()

    def __len__(self):
        return len(self.hosts)


class InventoryProvider(BasePlugin):

    def host_group_breakdown(self, category):
        """
        Returns a list of groups belonging to a category.
        Example: if category = "datacenter", an expected return value would be ["us-east-1", "us-west-2"]
        :param category: A category string to aggregate by
        :return: A list of HostCategory objects
        """
        raise NotImplementedError('override me')

    def list(self, category, group, sort_by=None, from_ind=None, to_ind=None):
        """
        Filter by a field and value.
        Example: provider.list("datacenter", "us-east-1") will return all Hosts in the us-east-1 datacenter
        :param category: Category to filter by (i.e. "datacenter")
        :param group: group to filter by (i.e. "us-east-1")
        :param sort_by: optional, a string representing a host attribute to sort by. hostname, for example
        :param from_ind: to support pagination, you may return only a subset of the results. this is the start index
        :param to_ind: to support pagination, you may return only a subset of the results. this is the end index
        :return: a list of Host objects
        """
        raise NotImplementedError('override me')

    def host_search(self, query, from_ind=None, to_ind=None):
        """
        Given a query string, perform a search of hosts
        :param query: a query string to perform the lookup by
        :param from_ind:  to support pagination, you may return only a subset of the results. this is the start index
        :param to_ind: to support pagination, you may return only a subset of the results. this is the end index
        :return: a list of Host objects
        """
        raise NotImplementedError('override me')

    def get_host_by_id(self, host_id):
        """
        Return a Host object by its ID
        :param host_id: a host ID to query by
        :return: a Host object
        """
        raise NotImplementedError('override me')
