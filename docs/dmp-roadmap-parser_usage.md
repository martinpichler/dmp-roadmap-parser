## DMP-Roadmap parser usage
In order to use the DMP-Roadmap parser please make sure you have a runnable version of *dmp-roadmap* on your system. Currently DMP-Roadmap parser only supports *postgreSQL* so make sure you choose the right database system when setting up *dmp-roadmap*. Since the setup instructions of the *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap)* repository are pretty outdated we created our own *[dmp-roadmap setup guide](dmp-roadmap_setup.md)*.

### Requirements
The project was developed with python 3.6 (64bit). In order to run dmp-parser some additional python packages have to be installed. They can be found in:
* *source/requirements.txt*
  to install all:
  ```bash
  pip install -r requirements.txt
  ```

### Usage
Using the DMP-Roadmap parser is as simple as adapting a config file and executing a python script.

First change the values in
* *source/parser.config*

accordingly to your information. The fields should be self explainatory. For the field "template" under the section [DMP] write either "horizon" to specify the template as Horizon2020 or "fwf" to specify the template to be parsed as FWF. The field "ID" is the id assigned to the DMP in *dmp-roadmap*

Execute the parser with
  ```bash
  python parser.py
  ```

the corresponding machine actionable dmp will be saved in
* *output/ma-dmps*


### Project Architecture (Implementation)
Two classes were created to parse the question in the template
* *source/DMPparser/horizon_parser.py* (HorizonParser)
* *source/DMPparser/fwf_parser.py* (FWFParser)

We have included tests for the parsers as jupyter notebooks:
* *tests/horizon2020_test.ipynb*
* *test/fwf_test.ipynb*

There you can play around with custom inputs and check what information the parser will retrieve.

The database access happens in the classes
* *source/DMPparser/dmp_horizon_parser.py* (DMPHorizonParser)
* *source/DMPparser/dmp_fwf_parser.py* (DMPFWFParser)

DMPHorizonParser/DMPFWFParser retrieves the information from the database, removes/replaces the HTML tags (since the answers are stored as HTML in the database) and passes them on the the parser.

The entry point of the project is the class
* *source/parser.py* (DMPParser)

It reads in the config file
* *source/parser.config*

and passes on the information to either DMPHorizonParser or DMPFWFParser depending on the selected template.
