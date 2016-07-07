#! /bin/bash
# :Usage: bash scp_master_stratuslab.sh {add_master} {private_key_file}
# Scp to a stratuslab instance (Ubuntu 14.04) files needed to deploy the master 
# with {add_master} address of the master and 
# {private_key_file} file of the private key to connect to ScienceFS account (with absolute path)

ADD_MASTER=$1
SCIENCEFS_KEY=$2
# Make it possible to log in as root
ssh ubuntu@"$ADD_MASTER" 'bash -s' < root_permissions.sh
# Copy sciencefs key and install scipt
scp env.sh deploy_master_stratuslab.sh root@"$ADD_MASTER":/root/
scp $SCIENCEFS_KEY root@"$ADD_MASTER":/root/.ssh/id_rsa_sciencefs
