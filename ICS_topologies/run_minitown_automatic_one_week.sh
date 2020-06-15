#!/bin/bash
echo "Running week " $1

if [ ! -d minitown_topology_dataset_generation/logs ]; then\
   mkdir minitown_topology_dataset_generation/logs;\
fi

if [ ! -d minitown_topology_dataset_generation/output ]; then\
   mkdir minitown_topology_dataset_generation/output;\
fi

cd minitown_topology_dataset_generation; rm -rf minitown_db.sqlite; python init.py; sudo chown mininet:mininet minitown_db.sqlite
sudo pkill  -f -u root "python -m cpppo.server.enip"
sudo mn -c
sudo python automatic_run.py $1