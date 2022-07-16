from pyowm.owm import OWM
from pyowm.utils.config import get_config_from
from pyowm.commons.exceptions import NotFoundError
config_dict = get_config_from('./owmconfig.json')
owm = OWM('6e0d73131fde98fc9c01f5ae5d5db3b1', config_dict)
mgr = owm.weather_manager()

def get_weather(city: str):
	observation = mgr.weather_at_place(city)
	print(observation.weather.detailed_status)
