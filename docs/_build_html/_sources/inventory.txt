.. _inventory:

Inventory Providers
===================

GRU supports pluggable inventory providers. Inventory providers fill in the list of hosts that make up GRU's view of the world.
They allow grouping, listing and searching for hosts, as well as provide metadata for every host in the inventory.

Out of the box, GRU provides two different inventory providers: an ElasticSearch_ provider that assumes hosts appear
as documents in an ElasticSearch cluster; and an EC2 provider that queries the `AWS EC2 API`_

Configuring an Inventory Provider
---------------------------------

at the most basic level, you need to set the :ref:`inventory.provider <inventory-provider>` configuration parameter to a fully qualified
class name of a class that implements an inventory provider.


ElasticSearch Provider
----------------------

The ElasticSearch_ provider assumes that you have configured an ElasticSearch cluster with an index containing
hosts as documents. The document IDs in the index correlate to host IDs, and the documents are JSON encoded dictionaries of host metadata.

It's actually pretty simple to create such an index.
See the provided `mapping file`_ and an `example script that populates the hosts index`_

To enable the ElasticSearch provider, please use ``gru.contrib.inventory.providers.ElasticSearchProvider`` as the value for ``inventory.provider``
and refer to the :ref:`provider documentation <config-params-es-provider>`.

Here's a snippet of such a configuration:

.. code-block:: yaml

    ---
    inventory:
      provider: gru.contrib.inventory.providers.ElasticSearchProvider
      config:
        index: gru-inventory
        timeout_seconds: 10
        hosts:
          # HTTP endpoints to your elasticsearch clusters.
          # No need to specify all servers, they are used for discovery
          - http://10.0.0.1:9200
          - http://10.0.0.2:9200
      ...


EC2 Provider
------------

To enable the EC2 provider, please use ``gru.contrib.inventory.providers.EC2Proivder`` as the value for ``inventory.provider``
and refer to the :ref:`provider documentation <config-params-ec2-provider>`.

The EC2 provider supports aggregation of hosts from several different AWS accounts and/or regions.

Here's a snippet of such a configuration:

.. code-block:: yaml

    ---
    provider: gru.contrib.inventory.providers.EC2Provider
    config:
      accounts:
        - aws_access_key_id: AKXXXXXXXXXXXXXXXXXX
          aws_secret_access_key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
          regions: ['us-east-1', 'us-west-2']


Writing your own
----------------


Writing an inventory provider is covered under :ref:`Writing your own inventory providers <plugin_dev_inventory_providers>`


.. _AWS EC2 API: http://docs.aws.amazon.com/AWSEC2/latest/APIReference/Welcome.html
.. _ElasticSearch: https://www.elastic.co/products/elasticsearch
.. _mapping file: http://github.com/similarweb/gru/scripts/elasticsearch/mapping.json
.. _example script that populates the hosts index: http://github.com/similarweb/gru/scripts/elasticsearch/facter_inventory.py
