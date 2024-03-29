import importlib
import json
import logging
import sys
import threading

from bottle import run, request, response, Bottle

from utils.json_http_response import generate_sensor_representation, generate_api_response, generate_sensor_capabilities
from virtual_sensor import VirtualSensor


# Helper function and check of the arguments supplied
def usage():
    """ Print short help """
    print("#################################################################")
    print("#                                                               #")
    print("# iQAS: an integration platform for QoO Assessment as a Service #")
    print("# Module: Virtual Sensor Container                              #")
    print("# (C) 2017 Antoine Auger                                        #")
    print("#                                                               #")
    print("#################################################################\n")

# Loading the configuration
with open('../etc/sensor.config') as config_file:
    config = json.load(config_file)

# Loading the capabilities of the virtual sensor
with open('../etc/capabilities.config') as capabilities_file:
    capabilities = json.load(capabilities_file)


# Bottle parameters
app = Bottle()
bottle_host = "0.0.0.0"  # To listen on all interfaces
bottle_port = 8080
sensor_id = str(sys.argv[1])
mode = str(sys.argv[2])
publish_to = str(sys.argv[3])
obs_generation_mode = str(sys.argv[4])
sensor = VirtualSensor(sensor_id=sensor_id)
sensor_endpoint = str(bottle_port) + '/' + sensor_id


# REST APIs for the virtual sensor (see also the corresponding class virtual_sensor.py)
@app.route('/' + sensor_id, method='GET')
def init_virtual_sensor():
    """ Return an overview of the specified virtual sensor """
    return generate_sensor_representation(response, sensor)


@app.route('/' + sensor_id + '/enabled', method='GET')
def get_sensor_enabled():
    json_response = generate_api_response(response,
                                          result="OK",
                                          details="",
                                          capability="enabled",
                                          old_value="",
                                          value=sensor.enabled)
    return json_response


@app.route('/' + sensor_id + '/enabled', method='POST')
def set_sensor_enabled():
    request_json_body = json.loads(request.body.read().decode('UTF-8'))
    old_value = sensor.enabled
    value = request_json_body['value']
    if type(value) == bool:
        sensor.enable_sensor(value)
        json_response = generate_api_response(response,
                                              result="OK",
                                              details="",
                                              capability="enabled",
                                              old_value=old_value,
                                              value=value)
    else:
        json_response = generate_api_response(response,
                                              result="NOK",
                                              details="Only one boolean is accepted for this POST request. "
                                                      "E.g.: {'value': true}")
    return json_response


@app.route('/' + sensor_id + '/sensing', method='GET')
def get_sensor_sensing():
    json_response = generate_api_response(response,
                                          result="OK",
                                          details="",
                                          capability="sensing",
                                          old_value="",
                                          value=sensor.sensing)
    return json_response


@app.route('/' + sensor_id + '/sensing', method='POST')
def set_sensor_sensing():
    request_json_body = json.loads(request.body.read().decode('UTF-8'))
    old_value = sensor.enabled
    value = request_json_body['value']
    if type(value) == bool:
        result, details = sensor.enable_sensing_process(value)
        json_response = generate_api_response(response,
                                              result=result,
                                              details=details,
                                              capability="sensing",
                                              old_value=old_value,
                                              value=value)
    else:
        json_response = generate_api_response(response,
                                              result="NOK",
                                              details="Only one boolean is accepted for this POST request. "
                                                      "E.g.: {'value': true}")
    return json_response


@app.route('/' + sensor_id + '/urlPublishObs', method='GET')
def get_sensor_url_publish():
    json_response = generate_api_response(response,
                                          result="OK",
                                          details="",
                                          capability="url_publish_obs",
                                          old_value="",
                                          value=sensor.publish_to)
    return json_response


@app.route('/' + sensor_id + '/urlPublishObs', method='POST')
def set_sensor_url_publish():
    request_json_body = json.loads(request.body.read().decode('UTF-8'))
    old_value = sensor.enabled
    value = request_json_body['value']
    if type(value) == str:
        result, details = sensor.set_url_to_publish(value)
        json_response = generate_api_response(response,
                                              result=result,
                                              details=details,
                                              capability="url_publish_obs",
                                              old_value=old_value,
                                              value=value)
    else:
        json_response = generate_api_response(response,
                                              result="NOK",
                                              details="Only a well formed URL is accepted for this POST request. "
                                                      "E.g.: {'value': 'http://localhost:8080'}")
    return json_response


@app.route('/' + sensor_id + '/capabilities', method='GET')
def get_sensor_details():
    """ Return the different capabilities of the specified virtual sensor """
    return generate_sensor_capabilities(response, sensor)


@app.route('/' + sensor_id + '/capabilities/<capability>', method='GET')
def get_sensor_capability(capability):
    """ Method to get a sensor parameter (capability) """
    result, details, value = sensor.get_capability(capability)
    json_response = generate_api_response(response,
                                          result=result,
                                          details=details,
                                          capability=capability,
                                          old_value="",
                                          value=value)
    return json_response


@app.route('/' + sensor_id + '/capabilities/<capability>', method='POST')
def set_sensor_capability(capability):
    """ Method to modify a sensor parameter (capability) """
    request_json_body = json.loads(request.body.read().decode('UTF-8'))
    result, details, old_value = sensor.get_capability(capability)
    value = request_json_body['value']
    if result == "OK":
        result, details = sensor.set_capability(capability, value)
    json_response = generate_api_response(response,
                                          result=result,
                                          details=details,
                                          capability=capability,
                                          old_value=old_value,
                                          value=value)
    return json_response

config['publish_to'] = publish_to
config['mode'] = mode
config['obs_generation_mode'] = obs_generation_mode
if len(sys.argv) == 6:
    config['trust'] = int(sys.argv[5])

if obs_generation_mode == 'ADAPTER':
    config['trust'] = 100
    config['adapter_file'] = sys.argv[5]
    config['adapter_class'] = sys.argv[6]
    config['endpoint_options'] = sys.argv[7]

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) < 5 or len(sys.argv) > 8:
        usage()
        print('ERROR: Wrong number of parameters')
        exit()
    else:
        # Start of a bottle server to handle calls to the sensor API
        if config['obs_generation_mode'] != 'ADAPTER' or (config['obs_generation_mode'] == 'ADAPTER' and config['adapter_file'] != 'hint_rabbitmq'):
            threading.Thread(target=run, kwargs=dict(app=app, host=bottle_host, port=bottle_port, quiet=True, reloader=False)).start()

        logging.warning("Virtual sensor '{}' successfully deployed".format(sensor_id))

        # Virtual sensor creation
        sensor.set_config(enabled=True,
                          config=config,
                          mode=mode,
                          capabilities=capabilities)
