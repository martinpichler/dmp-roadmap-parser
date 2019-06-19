import configparser
import json
from DMPparser.dmp_horizon_parser import DMPHorizonParser
from DMPparser.dmp_fwf_parser import DMPFWFParser

config = configparser.ConfigParser()
config.sections()
config.read('parser.config')

if config["DMP"]["template"] == "horizon":
    hp = DMPHorizonParser(config["DB"]["dbuser"], config["DB"]["dbpassword"], config["DB"]["dbhost"], config["DB"]["dbport"], config["DB"]["dbname"],config["DMP"]["id"])
    
    with open("../output/ma-dmps/"+config["DMP"]["id"]+".json", 'w') as outfile:  
        outfile.write(hp.parse())
    
elif config["DMP"]["template"] == "fwf":
    fwfp = DMPFWFParser(config["DB"]["dbuser"], config["DB"]["dbpassword"], config["DB"]["dbhost"], config["DB"]["dbport"], config["DB"]["dbname"],config["DMP"]["id"])
    with open("../output/ma-dmps/"+config["DMP"]["id"]+".json", 'w') as outfile:  
        outfile.write(fwfp.parse())
else:
    print("Invalid Confguration")