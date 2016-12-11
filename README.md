## GRU

GRU is a host-centric inventory management system. It is used to visualize and provide context on individual servers
and more importantly, on groups of servers.

It was designed in order to help operations teams, as well as developers to better understand their infrastructure
and to provide a unified view of available compute resources.

### Basic Configuration

Before we can run GRU, we need to setup a yaml file describing how to access our inventory
and optionally how to authenticate and authorize users as well as set other configuration parameters to adjust GRU to our liking.

Here's a very basic example of how this configuration might look like, without any authentication or authorization:

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

### Run using Docker

Assuming you've already created a configuration file and named it `gru.yaml`, simply run the docker image:

    $ docker run --rm -it \
        -v $PWD:/etc/gru \
        -e GRU_SETTINGS=/etc/gru/gru.yaml \
        -e "AWS_ACCESS_KEY_ID=AKXXXXXXXXXXXXXXXXXX" \  # Set this to your AWS keys
        -e "AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
        -p 5000:5000 \
        similarweb/gru:latest

### Where to go from here

For more information on running, configuring and extending GRU with plugins, check out http://gru.readthedocs.com/

