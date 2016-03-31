#! /bin/bash
# :Usage: bash scp_master_stratuslab.sh {add_master}
# Scp to a stratuslab instance (Ubuntu 14.04) files needed to deploy the master 
# with {add_master} address pf the master

ADD_MASTER=$1
scp env.sh deploy_master_stratuslab.sh root@"$ADD_MASTER":/root/.
