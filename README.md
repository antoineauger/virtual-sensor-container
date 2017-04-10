# virtual-sensor-container
A shippable 'virtual sensor'`container for the iQAS platform.

### Building the virtual sensor container
Inside the resources root directory (`virtual-sensor-container`), type the following command:
```
$ docker build -t antoineog/docker-virtual-sensor .
```

Note: by default, the virtual sensor use a raw temperature dataset from Aarhus. 
If you want to specify your own raw observation file, copy it in the `virtual_sensors/data` directory and add the `--build-arg obsFile=[PATH-TO-YOUR-FILE]` option.
For instance:
```
$ docker build --build-arg obsFile=data/my_data_file.txt -t antoineog/virtual-sensor-container .
```

### Running the virtual sensor container
The generic command is:
```
$ docker run -p 127.0.0.1:PORT:8080 antoineog/virtual-sensor-container ID MODE PUBLISH-TO OBS-GENERATION [TRUST]
```

You should specify the following MANDATORY and [OPTIONAL] arguments:

* `PORT`: The port you want the virtual sensor will be listening to on localhost (to send API requests)
* `ID`: The name of the virtual sensor
* `MODE`: `KAFKA` if you want to publish to a Kafka topic, `REST if you want to POST observation on a listening endpoint
* `PUBLISH-TO`: The URL or the Kafka topic where the virtual sensor has to send its observations
* `OBS-GENERATION`: Accepted values are `FILE`, `FILE_WITH_CURRENT_DATE`, `"[-5.0,5.0]"` or `RANDOM`
* `[TRUST]`: An integer in the range 0-100 that indicates how accurate should be the sensor. 0 = all observations are inaccurate (out of the measurement range), 100 = all observations are accurate. 
This parameter is optional and should be used in combination with `RANGE` and `RANDOM` observation generation modes only.

For instance, following commands are valid:
```
$ docker run -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container sensor01 REST http://10.161.3.183:8081/publish/observation "[-2,5]"
```

```
$ docker run -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container sensor01 KAFKA temperature "[-2,5]"
```

```
$ docker run -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container sensor01 KAFKA temperature "[-100.0,50.0]" 50
```

To exit the container, just press `CTRL` + `C`.

Instead, if you prefer to run the docker container in background (in detached mode), just add the `-d` option:
```
$ docker run -d -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container "sensor01" "http://10.161.3.183:8081/publish/observation"
```

### Managing the virtual sensor container

The following are a quick remainder of basic docker commands.

You can see docker containers and their statuses by running `docker ps`. 
```
$ docker ps
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS              PORTS                      NAMES
0657fb1624c3        antoineog/virtual-sensor-container   "/usr/bin/python3 /ho"   47 seconds ago      Up 51 seconds       127.0.0.1:9092->8080/tcp   prickly_roentgen
```
Note: use the command `docker ps -a` if the list is empty or if you do not find your container.

To stop a given container, just type the following command:
```
$ docker stop prickly_roentgen
prickly_roentgen
```

Now the container is stopped, you can remove it:
```
$ docker rm prickly_roentgen
prickly_roentgen
```
