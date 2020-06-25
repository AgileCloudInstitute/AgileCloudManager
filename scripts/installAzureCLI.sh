#!/bin/bash

sudo yum install yum-utils
if [[ $(sudo yumdownloader azure-cli) == *".rpm"* ]]; then 
  sudo rpm -ivh --nodeps $(sudo yumdownloader azure-cli)
  echo "Woo Hoo!" 
fi
