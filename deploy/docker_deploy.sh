#!/bin/bash

set -e

if [ "$#" -lt 1 ]; then
    echo "Illegal number of parameters"
else
	MODE=$1

	if [[ "$MODE" == "BUILD" ]]; then
		echo '>>> Building new image'
		# Due to a bug in Docker we need to analyse the log to find out if build passed (see https://github.com/dotcloud/docker/issues/1875)
		docker build --build-arg obsFile=data/raw_observations.txt -t antoineog/docker-virtual-sensor . | tee /tmp/docker_build_result.log
		RESULT=$(cat /tmp/docker_build_result.log | tail -n 1)
		if [[ "$RESULT" != *Successfully* ]];
		then
		  exit -1
		fi

	elif [[ "$MODE" == "DEPLOY" ]]; then
		echo '>>> Starting new container'
		docker run -d -p 127.0.0.1:10092:8080 antoineog/docker-virtual-sensor "sensor02" "KAFKA" "temperature"

	elif [[ "$MODE" == "CLEAN" ]]; then
		if [ "$#" -eq 2 ]; then
    		FORCE=$2

    		if [[ "$FORCE" == "-f" ]]; then
    			echo '>>> Cleaning up containers with force option'
				docker ps -a | grep "antoineog/docker-virtual-sensor" | awk '{print $1}' | while read -r id ; do
					#docker stop $id
					docker rm $id -f
				done
			else
				echo '>>> Cleaning up containers'
				docker ps -a | grep "Exit" | awk '{print $1}' | while read -r id ; do
					docker rm $id
				done
    		fi
    	fi	 
		echo '>>> Cleaning up images'
		docker images | grep "^<none>" | head -n 1 | awk 'BEGIN { FS = "[ \t]+" } { print $3 }'  | while read -r id ; do
			docker rmi $id
		done
	fi
fi
