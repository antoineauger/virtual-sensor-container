#!/bin/bash

set -e

echo "###################################################################"
echo "#  iQAS: an integration platform for QoO Assessment as a Service  #"
echo "#                                                                 #"
echo "#                     (C) 2017 Antoine Auger                      #"           
echo "###################################################################"
echo ""

if [ "$#" -lt 1 ]; then
    echo "Illegal number of parameters"
else
	MODE=$1

	if [[ "$MODE" == "BUILD" ]]; then
		echo '>>> Building new image'
		# Due to a bug in Docker we need to analyse the log to find out if build passed (see https://github.com/dotcloud/docker/issues/1875)
		docker build --build-arg obsFile=data/raw_observations.txt -t antoineog/docker-virtual-sensor ../. | tee /tmp/docker_build_result.log
		RESULT=$(cat /tmp/docker_build_result.log | tail -n 1)
		if [[ "$RESULT" != *Successfully* ]];
		then
		  exit -1
		fi

	elif [[ "$MODE" == "DEPLOY" ]]; then
		echo '>>> Starting containers according to the config file [deployment_options.config]'
		echo ''

		regex='([0-9]+):([0-9]+) (.*)'
		while IFS='' read -r line || [[ -n "$line" ]]; do
			if [[ $line =~ $regex ]]; then
		    	INDEX_START=${BASH_REMATCH[1]}
		    	INDEX_END=${BASH_REMATCH[2]}
		    	TOPIC=${BASH_REMATCH[3]}

		    	for i in `seq $INDEX_START $INDEX_END`; do
		        	PORT_NUMBER="10"
		        	PRETTY_PORT_NUMBER=""
		        	if [[ $i -lt 10 ]]; then
						PORT_NUMBER=$PORT_NUMBER"09"
						PRETTY_PORT_NUMBER="0"
					else
						PORT_NUMBER=$PORT_NUMBER"1"
		        	fi
					PORT_NUMBER+=$i
					PRETTY_PORT_NUMBER+=$i
					echo "Deploying sensor$PRETTY_PORT_NUMBER for $TOPIC [ http://127.0.0.1:$PORT_NUMBER/sensor$PRETTY_PORT_NUMBER ]"
					docker run -d -p 127.0.0.1:$PORT_NUMBER:8080 antoineog/docker-virtual-sensor "sensor"$PRETTY_PORT_NUMBER "KAFKA" $TOPIC
					echo "---"
		        done  
		    fi
		done < "docker_options.config"

	elif [[ "$MODE" == "CLEAN" ]]; then
		if [ "$#" -eq 2 ]; then
    		FORCE=$2

    		if [[ "$FORCE" == "-f" ]]; then
    			echo '>>> Cleaning up containers with force option'
				docker ps -a | grep "antoineog/docker-virtual-sensor" | awk '{print $1}' | while read -r id ; do
					docker rm $id -f
				done

				echo '>>> Cleaning up images'
				docker images | grep "^<none>" | head -n 1 | awk 'BEGIN { FS = "[ \t]+" } { print $3 }'  | while read -r id ; do
					docker rmi $id -f
				done
			fi
		else
			echo '>>> Stopping and cleaning up containers'
			docker ps -a | grep "antoineog/docker-virtual-sensor" | awk '{print $1}' | while read -r id ; do
				docker stop $id
				docker rm $id
			done

			echo '>>> Cleaning up images'
			docker images | grep "^<none>" | head -n 1 | awk 'BEGIN { FS = "[ \t]+" } { print $3 }'  | while read -r id ; do
				docker rmi $id
			done
    	fi	 
	fi
fi
