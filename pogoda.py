from pyowm.owm import OWM
from pyowm.utils.config import get_config_from
from pyowm.commons.exceptions import NotFoundError
from dotenv import load_dotenv
import os

load_dotenv()

config_dict = get_config_from('./owmconfig.json')
owm = OWM(os.environ("OWM_TOKEN",""), config_dict)
mgr = owm.weather_manager()

def get_weather(city: str):
	return mgr.weather_at_place(city)
