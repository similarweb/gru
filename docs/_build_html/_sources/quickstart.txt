.. _quickstart:

Quick Start
===========


Installation
------------

There are two ways to get started with GRU: Either clone the project and run the python server -
or run it using the the Docker image.

We recommend using Docker, since it eliminates the need to install all the different python and OS dependencies.

If you plan on contributing or simply hacking on GRU itself, you should probably use the local server instead.
Keep in mind that GRU provides a pretty flexible plugin system. You can develop your own plugins and keep using the docker image.


Basic Configuration
-------------------

Before we can run GRU, we need to setup a yaml file describing how to access our inventory
and optionally how to authenticate and authorize users as well as set other configuration parameters to adjust GRU to our liking.

Here's a very basic example of how this configuration might look like, without any authentication or authorization:

.. code-block:: yaml

    ---
    flask:
      # Keep this one random. used by the session system.
      secret_key: 'fojegj340fuccotnhvi39yombpris'

    # Here we set up EC2 as our source of inventory.
    inventory:
      provider: gru.contrib.inventory.providers.EC2Provider
      config:
       accounts:
          # setting aws_access_key and aws_secret_access_key is optional
          # otherwise, will be taken from ~/.aws/credentials
          # or environment variables
          - regions: ['us-east-1']
      # Whiche metadata field to use as a hostname
      host_display_name_field: tag:Name
      # Fields to create logical groups of hosts by
      group_by:
        - field: tag:stack
          title: Stack
        - field: tag:role
          title: Role
        - field: region
          title: Region
      # Fields visible when showing a table of hosts
      host_table_fields:
        - field: tag:role
          title: Role
        - field: tag:environment
          title: Env
        - field: architecture
          title: Arch
        - field: instance-state-name
          title: Status
        - field: private-ip-address
          title: IP
      # Fields visible by default when looking at a single host
      # (The user can toggle to view remaining fields)
      host_info_fields:
        - field: tag:role
          title: Role
        - field: region
          title: DC
        - field: tag:environment
          title: Env
        - field: architecture
          title: Arch
        - field: instance-state-name
          title: Status
        - field: private-ip-address
          title: IP


Please review the :ref:`Configuration Reference <configuration>` section or check out the ``examples/`` directory on Github_.


Running using Docker
--------------------

Assuming you already have a yaml configuration file named ``gru.yaml``, all we need to do is run the docker image:

.. code-block:: bash

    $ docker run --rm -it \
        -v $PWD:/etc/gru \
        -e GRU_SETTINGS=/etc/gru/gru.yaml \
        -e "AWS_ACCESS_KEY_ID=AKXXXXXXXXXXXXXXXXXX" \  # Set this to your AWS keys
        -e "AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
        -p 5000:5000 \
        similarweb/gru:latest

If you are using custom plugins, simply mount the module directory and reflect that in your settings file:

.. code-block:: bash

    $ docker run --rm -it \
        -v $PWD:/etc/gru \
        -e GRU_SETTINGS=/etc/gru/gru.yaml \
        -e "AWS_ACCESS_KEY_ID=AKXXXXXXXXXXXXXXXXXX" \  # Set this to your AWS keys
        -e "AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
        -v /path/to/plugins:/opt/gru-plugins \
        -p 5000:5000 \
        similarweb/gru:latest
  
This will automatically pull the gru image from docker hub, and run a server using the ``gru.yaml`` settings file.


Running a local server
----------------------

Running a local server has been tested on Debian and Ubuntu linux.
It should be able to run on OSX and Windows as well, but it hasn't been thoroughly tested.

First, install GRU's dependencies:

.. code-block:: bash

    $ apt-get install --no-install-recommends \
        python-dev \
        libssl-dev \
        libsasl2-dev \
        libldap2-dev

Once that's done, we need to clone the GRU project:

.. code-block:: bash

    $ git clone git://github.com/similarweb/gru .

Then, install all the required Python dependencies.
Preferably, this step should be done in a virtualenv_):

.. code-block:: bash

    $ pip install -r requirements.txt

Now, run the server itself using the settings file you created:

.. code-block:: bash

    $ GRU_SETTINGS="/path/to/gru.yaml" python app.py runserver

A server will be started, listening on http://localhost:5000


.. _Github: http://www.github.com/similarweb/gru
.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/