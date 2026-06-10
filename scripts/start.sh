#!/bin/bash
docker run -it --name mlopssec -p 5000:5000 -p 8080:8080 -p 8081:8081 -p 8180:8180 -p 8888:8888 \
               -d -v .:/home/jovyan/mlopssec:rw omegaml/mlopssec bash || echo "INFO: Already running"
