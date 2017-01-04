import requests
import os
from bottle import Bottle


class WebApp(Bottle):
    """
    Open a HTTP/TCP Port and spit out json response.
    """
    def __init__(self, sdc, cfg, envlist):
        self.sdc = sdc
        self.weather_server_ip = cfg.get("weather", "server")
        self.weather_server_port = cfg.get("weather", "port")
        self.weather_api_key = cfg.get("weather", "apikey")
        self.zipcode = cfg.get("weather", "zipcode")
        self.country = cfg.get("weather", "country")
        self.city = cfg.get("weather", "city")
        Bottle.__init__(self)
        self.route("/help", callback=self.show_help)
        self.route("/", callback=self.index)
        self.route("/alarms", callback=self.alarms)
        self.route("/reset", callback=self.reset_alarms)
        self.route("/weather", callback=self.weather)
        self.route("/hello", callback=self.hello)
        self.route("/env", callback=self.show_env)
        self.envlist = envlist

    def show_help(self):
        return (
                "/help   : show this message.\n" +
                "/       : show the snapshot.\n" +
                "/alarms : show the alamrs.\n" +
                "/reset  : reset the alamrs.\n" +
                "/weather: show wather data.\n" +
                "/hello  : say hello.\n" +
                "/env    : show CAF env.\n"
                )

    def hello(self):
        return {"msg": "hello"}

    def index(self):
        return self.sdc.get_snapshot()

    def alarms(self):
        return self.sdc.get_alarms()

    def reset_alarms(self):
        return self.sdc.reset_alarms()

    def weather(self):
        url = '{SERVER}:{PORT}/api/{APIKEY}/conditions/q'.format(
            SERVER=self.weather_server_ip,
            PORT=self.weather_server_port,
            APIKEY=self.weather_api_key
        )
        if self.zipcode:
            url = url + '/{ZIPCODE}.json'.format(
                ZIPCODE=self.zipcode
            )
        elif self.country and self.city:
            url = url + '/{COUNTRY}/{CITY}.json'.format(
                COUNTRY=self.country,
                CITY=self.city
            )
        else:
            raise Exception('ERROR: zipcode or country/city must be specified.')

        r = requests.get(url)
        if r.ok:
            if r.headers["content-type"] == "application/json":
                return r.json()
            return r.text
        else:
            raise Exception("Error reading weather data. Upstream server returned %s" % r.status_code)

    def show_env(self):
        r = '{\n'
        for l in self.envlist:
            r = r + '\t"%s":"%s"\n' % (l, os.getenv(l))
        r = r + '}\n'

        return r

