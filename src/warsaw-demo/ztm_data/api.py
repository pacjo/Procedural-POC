import os
import json
import requests

import atexit

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

_cache_file = 'api_cache.json'
_cache = {}

def _load_cache():
	"""Loads the cache from a JSON file."""
	global _cache

	if os.path.exists(_cache_file):
		try:
			with open(_cache_file, 'r') as f:
				_cache = json.load(f)
				print("Cache loaded from file.")
		except json.JSONDecodeError:
			print("Cache file is invalid, using empty cache")

	else:
		print("Cache file does not exist, starting with empty cache")

def _save_cache():
	"""Saves the cache to a JSON file."""

	with open(_cache_file, 'w') as f:
		json.dump(_cache, f, indent=4)

	print("Cache saved to file.")

# Load cache on module load
_load_cache()

# Save cache when module is unloaded
atexit.register(_save_cache)

def get_api_key():
	"""Retrieves the API key from the .env file."""
	api_key = os.environ.get('API_KEY')

	if not api_key:
		print("Error: The 'API_KEY' variable is not set in the .env file.")
		exit()

	return api_key

def get_stop_data(api_key):
	"""Fetches ZTM stop data from the API, using cache."""

	cache_key = 'stops_data'
	if cache_key in _cache:
		print("Using cached stops data")
		return _cache[cache_key]

	print("Fetching stops data from API")
	response = requests.get(f'https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&api_key={api_key}')
	data = response.json()
	_cache[cache_key] = data

	return data

def get_routes_data(api_key):
	"""Fetches ZTM routes data from the API, using cache."""

	cache_key = 'routes_data'
	if cache_key in _cache:
		print("Using cached routes data")
		return _cache[cache_key]

	print("Fetching routes data from API")
	response = requests.get(f'https://api.um.warszawa.pl/api/action/public_transport_routes/?apikey={api_key}')
	data = response.json()
	_cache[cache_key] = data

	return data

def save_data_to_file(data, filename: str):
	"""Saves data to a JSON file."""

	with open(filename, 'w') as file:
		json.dump(data, file, indent=4)

def load_data_from_file(filename: str):
	"""Loads data from a JSON file."""

	with open(filename, 'r') as file:
		return json.load(file)

def clear_cache():
	"""Clears the cache."""

	global _cache
	_cache = {}

	if os.path.exists(_cache_file):
		os.remove(_cache_file)
	print("Cache cleared.")
