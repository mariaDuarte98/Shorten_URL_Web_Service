# Shorten URL Web Service

Index
- [Shorten URL WebService](#shorten-url-web-service)
- [Getting Started](#getting-started)
- [Requirements](#requirements)
- [Testing](#testing)
  - [Test Coverage](#test-coverage)
- [Thank you!](#thank-you)


Hi! This is the source code for a simple shorten urls web service.
It consists of a Flask application, which uses the 3 following endpoints:

- POST /shorten
- GET /&lt;shortcode&gt;
- GET /&lt;shortcode&gt;/stats


# Getting Started

*This configuration process was done using `python3.9`, and the package manager `pip`.*

First let's proceed with creating a virtual environment, to install all needed python packages.
We can use `virtualenv` tool, which can be installed using `pip`, with the command `pip install virtualenv`. 

To create a virtual environment for the project, type the following commands: 
- `cd Shorten_Url_Web_Service/`
- `virtualenv venv`

To activate the venv created type:

- `source venv/bin/activate`

To leave the venv type:

- `deactivate`

## Requirements

All required packages are in the `requirments.txt` file. To installed them, simply type `pip install -r requirments.txt`
 
## Run the application
First you will need to initialize the database. Inside the project directory run:
```
 python init_db.py
```

Then to start the application run:
```
 python shorten_url_service.py 
```

## Testing

Inside the project directory run the following command to test the full class:
```
 python -m unittest test.test_shorten_url_service
```

To run a specific test, do:
```
 python -m unittest test.test_shorten_url_service.ShortenURLServiceTest.test_shorten_no_url
```
### Test Coverage

First, run the coverage module:
```
python -m coverage run -m unittest
```

Then turn the coverage data generated earlier into a report:
```
python -m coverage report
```

To view in html format:
```
python -m coverage html 
```

# Thank you!

Thank you, and hope you enjoyed the web service. :)

[![Maria Duarte Linkedin](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maria-duarte-92298b17b/)
