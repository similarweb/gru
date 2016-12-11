from gru.config import settings
from gru.plugins.base.inventory import InventoryProvider, Host, HostCategory, HostList
from elasticsearch import Elasticsearch, NotFoundError


class ElasticSearchProvider(InventoryProvider):

    def __init__(self, *args, **kwargs):
        super(ElasticSearchProvider, self).__init__(*args, **kwargs)
        self.es = None

    def on_load(self):
        self.es = Elasticsearch(
            hosts=settings.get('inventory.config.hosts'),
            timeout=settings.get('inventory.config.timeout_seconds', 30))

    @staticmethod
    def get_search_kwargs(from_ind=None, to_ind=None):
        search_kwargs = {
            'index': settings.get('inventory.config.index'),
            'size': settings.get('inventory.default_result_size', 50)
        }
        doc_type = settings.get('inventory.config.document_type')
        if doc_type is not None:
            search_kwargs['doc_type'] = doc_type
        if from_ind:
            search_kwargs.update({'from_': from_ind})
        return search_kwargs

    def host_group_breakdown(self, category):
        search_kwargs = self.get_search_kwargs()
        search_kwargs['body'] = {'size': 0, 'aggs': {category: {'terms': {'field': category, 'size': 0}}}}
        es_result = self.es.search(**search_kwargs)
        categories = []
        for term in es_result.get('aggregations', {}).get(category, {}).get('buckets', []):
            categories.append(HostCategory(
                category,
                term.get('key'),
                term.get('doc_count')))
        return categories

    def list(self, category, group, sort_by=None, from_ind=None, to_ind=None):
        query = {'query': {'term': {category: group}}}
        if sort_by:
            order = 'asc'
            if sort_by.startswith('-'):
                order = 'desc'
                sort_by = sort_by[1:]
            query['sort'] = [{sort_by: order}]
        search_kwargs = self.get_search_kwargs(from_ind, to_ind)
        search_kwargs['body'] = query
        es_result = self.es.search(**search_kwargs)
        hits = es_result.get('hits', {})
        hosts = HostList(total_hosts=hits.get('total'))
        for hit in hits.get('hits', []):
            hosts.append(Host(
                host_id=hit.get('_id'),
                host_data=hit.get('_source')))
        return hosts

    def host_search(self, query, from_ind=None, to_ind=None):
        search_kwargs = self.get_search_kwargs(from_ind, to_ind)
        query = {'query': {'query_string': {'query': query}}}
        sort_by = settings.get('inventory.host_table_sort_by', None)
        if sort_by:
            order = 'asc'
            if sort_by.startswith('-'):
                order = 'desc'
                sort_by = sort_by[1:]
            query['sort'] = [{sort_by: order}]
        search_kwargs.update({
            'body': query,
            'analyze_wildcard': True,
            'lowercase_expanded_terms': True,
        })
        es_result = self.es.search(**search_kwargs)
        hits = es_result.get('hits', {})
        hosts = HostList(total_hosts=hits.get('total'))
        for hit in hits.get('hits', []):
            hosts.append(Host(
                host_id=hit.get('_id'),
                host_data=hit.get('_source')))
        return hosts

    def get_host_by_id(self, host_id):
        search_kwargs = self.get_search_kwargs()
        search_kwargs['id'] = host_id
        del search_kwargs['size']
        try:
            es_result = self.es.get(**search_kwargs)
            return Host(host_id=host_id, host_data=es_result.get('_source', {}))
        except NotFoundError:
            return None
