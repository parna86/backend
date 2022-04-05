## SpikeWeb - backend

SpikeWeb's backend uses Flask. More specifically, it uses the  `flask_restful` package to structure the REST API. Currently, it is not hosted on a production server.

The repository contains a requirments.txt and environment.yml file which contain the dependencies for this project. To set up an environment with these, please refer to the [Conda documentation](https://medium.com/swlh/setting-up-a-conda-environment-in-less-than-5-minutes-e64d8fc338e4).

Clone this repository through your command line using 
``` git clone https://github.com/parna86/backend.git```

To run the project, enter the root directory and run `flask run`. This will start the development server. 


Common bugs: 
- The server is a production server - set the environment variable FLASK_ENV=development. 
