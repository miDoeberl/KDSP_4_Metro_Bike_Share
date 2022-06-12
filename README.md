# KDSP: Metro Bike Share Project



## Introduction

This repository contains the code for my final submission for the couse "Applied Data Science with Python".

## Running the code

* `Step 1:` Navigate to (this) the source directory:
	```bash
	$ cd <path-to-directory>
	```
* `Step 2:` Create a new virtual python environment:
	```bash
	$ python3.7 -m venv venv
	```
* `Step 3:` Activate the environment:
	```bash
	$ source venv/bin/activate
	```
* `Step 4:` Download the required python modules
	```bash
	$ pip install -r requirements.txt
	```
* `Step 5:` Run the program:
	```bash
	$ python main.py
	```

## Things to know
- When the code is run for the first time, the city map of Los-Angeles has to be downloaded which can take a few minutes. This is normal, don't exit the program. On subsequent launches a cached map is used.

## Usage
When the program has fully started, a new browser window should open up showing a map of the city of Los Angeles.
If this does not happen or you accidentally closed it, it can be manually opened at the URL http://127.0.0.1:8050.

If the map is now clicked, the closest bike stations where a bike can be rented are shown in green, while the closest bike stations where a bike can be returned are shown in orange.
If the map is clicked again, the shortest route between the two clicks is calculated, while passing two bike stations where a bike can be rented and returned.
A third click resets the state to the first click.

For additional information on a specific station, all bike station markers have a popup on click.