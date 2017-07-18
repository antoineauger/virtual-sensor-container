# virtual-sensor-container
A shippable "virtual sensor" container for the iQAS platform.

## The iQAS ecosystem

In total, 5 Github projects form the iQAS ecosystem:
1. [iqas-platform](https://github.com/antoineauger/iqas-platform) <br/>The QoO-aware platform that allows consumers to integrate many observation sources, submit requests with QoO constraints and visualize QoO in real-time.
2. [virtual-sensor-container](https://github.com/antoineauger/virtual-sensor-container) (this project)<br/>A shippable Virtual Sensor Container (VSC) Docker image for the iQAS platform. VSCs allow to generate observations at random, from file, or to retrieve them from the Web.
3. [virtual-app-consumer](https://github.com/antoineauger/virtual-app-consumer) <br/>A shippable Virtual Application Consumers (VAC) Docker image for the iQAS platform. VACs allow to emulate fake consumers that submit iQAS requests and consume observations while logging the perceived QoO in real-time.
4. [iqas-ontology](https://github.com/antoineauger/iqas-ontology) <br/>Ontological model and examples for the QoOonto ontology, the core ontology used by iQAS.
5. [iqas-pipelines](https://github.com/antoineauger/iqas-pipelines) <br/>An example of a custom-developed QoO Pipeline for the iQAS platform.

## System requirements

In order to correctly work, a virtual-sensor-container requires that the following software have been correctly installed and are currently running:
* Docker (see the [official website](https://www.docker.com/) for installation instructions)
* Apache Zookeeper `3.4.9` (when publishing to a `KAFKA` topic)
* Apache Kafka `0.10.2.0` (when publishing to a `KAFKA` topic)

## Project structure

```
project
│
└───data
│   │   raw_observations.txt
│
└───etc
│   │   capabilities.config
│   │   sensor.config
│
└───src
    └───adapters
    │   │   abstract_adapter.py
    │   │   open_weather_map_temp.py
    │   │   ...
    │
    └───utils
    │   │   json_http_response.py
    │   │   json_post_observations.py
    │   │   time_utils.py
    │
    │   main.py
    │   obs_generator.py
    │   virtual_sensor.py
```

## Building the virtual sensor container
Inside the resources root directory (`virtual-sensor-container`), type the following command:
```
$ docker build -t antoineog/virtual-sensor-container .
```

Note: by default, the virtual sensor use a raw temperature dataset from Aarhus.
If you want to specify your own raw observation file, copy it in the `virtual_sensors/data` directory and add the `--build-arg obsFile=[PATH-TO-YOUR-FILE]` option.
For instance:
```
$ docker build --build-arg obsFile=data/my_data_file.txt -t antoineog/virtual-sensor-container .
```

## Running the virtual sensor container
The generic command is:
```
$ docker run -p 127.0.0.1:PORT:8080 antoineog/virtual-sensor-container SENSOR_ID MODE PUBLISH-TO OBS-GENERATION [TRUST]
```
You should specify the following MANDATORY and [OPTIONAL] arguments:

* `PORT`: The port you want the virtual sensor will be listening to on localhost (to send API requests)
* `SENSOR_ID`: The name of the virtual sensor
* `MODE`: `KAFKA` if you want to publish to a Kafka topic, `REST` if you want to POST observation on a listening endpoint
* `PUBLISH-TO`: The URL or the Kafka topic where the virtual sensor has to send its observations
* `OBS-GENERATION`: Accepted values are `FILE`, `FILE_WITH_CURRENT_DATE`, `"[-5.0,5.0]"`, `RANDOM` or `ADAPTER`
* `[TRUST]`: An integer in the range 0-100 that indicates how accurate should be the sensor. 0 = all observations are inaccurate (out of the measurement range), 100 = all observations are accurate. This parameter is optional and should be used in combination with `RANGE` and `RANDOM` observation generation modes only.

If you use an adapter, the generic command is:
```
$ docker run -p 127.0.0.1:PORT:8080 antoineog/virtual-sensor-container SENSOR_ID MODE PUBLISH-TO "ADAPTER" ADAPTER-FILENAME ADAPTER-CLASSNAME ENDPOINT-OPTIONS
```
And you should specify the following MANDATORY arguments:
* `PORT`: The port you want the virtual sensor will be listening to on localhost (to send API requests)
* `SENSOR_ID`: The name of the virtual sensor
* `MODE`: `KAFKA` if you want to publish to a Kafka topic, `REST` if you want to POST observation on a listening endpoint
* `PUBLISH-TO`: The URL or the Kafka topic where the virtual sensor has to send its observations
* `ADAPTER-FILENAME`: The name of the Python file in the `/src/adapters` directory.
* `ADAPTER-CLASSNAME`: The class name to instantiate in the Python file specified in `ADAPTER-FILENAME`.
* `ENDPOINT-OPTIONS`: This corresponds to parameters for a given website, often located after the `?`. E.g., http://BASE_URL?param=ok.

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

```
$ docker run -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container sensor01 KAFKA temperature ADAPTER "open_weather_map_temp" "OpenWeatherMapTemp" "?q=London&appid=..."
```

To exit the container, just press `CTRL` + `C`.

Instead, if you prefer to run the docker container in background (in detached mode), just add the `-d` option:
```
$ docker run -d -p 127.0.0.1:9092:8080 antoineog/virtual-sensor-container sensor01 REST http://10.161.3.183:8081/publish/observation FILE
```

## Adding new adapters

You should place new adapters in the directory `/src/adapters`. When you create a new adapter, you should make it inherit from the AbstractAdapter class as follows:

```
from adapters.abstract_adapter import AbstractAdapter

class MyNewAdapter(AbstractAdapter):
    # Implement abstract methods of AbstractAdapter
```

You may have a look to the `open_weather_map.py` file for an example.

## Managing the virtual sensor container

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

## Acknowledgments

The iQAS platform have been developed during the PhD thesis of [Antoine Auger](https://personnel.isae-supaero.fr/antoine-auger/?lang=en) at ISAE-SUPAERO (2014-2017).

This research was supported in part by the French Ministry of Defence through financial support of the Direction Générale de l’Armement (DGA).

![banniere](https://github.com/antoineauger/iqas-platform/blob/master/src/main/resources/web/figures/banniere.png?raw=true "Banniere")
