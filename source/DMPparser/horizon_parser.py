import json
import re
import datefinder
from urllib.parse import urlparse

class HorizonParser():
    
    def __init__(self, dmp_title, dmp_description, dmp_created, dmp_modified, dmp_id, pi_name, pi_mail, pi_orcid):
        self.setup_dmp(dmp_title, dmp_description, dmp_created, dmp_modified, dmp_id, pi_name, pi_mail, pi_orcid)
    
    def setup_dmp(self, dmp_title, dmp_description, dmp_created, dmp_modified, dmp_id, pi_name, pi_mail, pi_orcid):
        self.dmp = {
            "dmp":{
                "title": dmp_title,
                "description":"Abstract::"+dmp_description,
                "created":dmp_created,
                "modified":dmp_modified,
                "dmp_id": {
                    "dmp_id": dmp_id,
                    "dmp_id_type": "HTTP-DOI"
                },
                "contact":{
                    "name": pi_name,
                    "mail": pi_mail,
                    "contact_id": {
                        "contact_id": pi_orcid,
                        "contact_id_type": "HTTP-ORCID"
                    }
                },
                "project": {}
            }
        }
    
    def __split_text_based_on_title(self, text):
        rep = {}
        for ds in self.dmp["dmp"]["dataset"]:
            title = ds["title"].lower()
            rep[title]=";"+title

        rep = dict((re.escape(k), v) for k, v in rep.items()) 
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text.lower()).split(";")
        return text
    
    def parse_question_1_1(self, text):
        if "description" in self.dmp["dmp"]["project"]:
            text=";State the purpose of the data collection/generation::"+text
            self.dmp["dmp"]["project"]["description"] += text
        else:
            text="State the purpose of the data collection/generation::"+text
            self.dmp["dmp"]["project"]["description"] = text
        return text
    
    def parse_question_1_2(self, text):
        if "description" in self.dmp["dmp"]:
            text=";Explain the relation to the objectives of the project::"+text
            self.dmp["dmp"]["description"] += text
        else:
            text="Explain the relation to the objectives of the project::"+text
            self.dmp["dmp"]["description"] = text
        return text
    
    def parse_question_1_3(self, text):
        rep = {"Title:": ";Title:", "Description:": ";Description:","Type:": ";Type:","Format:": ";Format:", "Source:":";Source:"}

        rep_lower = {}
        for k, v in rep.items():
            rep_lower[k.lower()]=v
        rep.update(rep_lower)    

        rep = dict((re.escape(k), v) for k, v in rep.items()) 
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

        datasets = []
        current_dataset = None
        current_format = None
        for line in text.split(";"):
            line = line.rstrip("\n\r")
            line = line.replace("\n","")
            if line.startswith("Title:"):

                line = line[7:] if line[6:].startswith(" ") else line[6:]

                if current_dataset != None:
                    if "distribution" not in current_dataset:
                        current_dataset["distribution"] = []
                        current_dataset["distribution"].append({"title":"Project"})
                    else:
                        if current_format != None:
                            for ds in current_dataset["distribution"]:
                                ds["format"] = current_format
                            current_format = None
                    current_dataset["metadata"] = []
                    current_dataset["technical_resource"] = []
                    datasets.append(current_dataset)
                current_dataset = {"title":line}

            if line.startswith("Description:"):
                if current_dataset != None:
                    line = line[13:] if line[12:].startswith(" ") else line[12:]
                    current_dataset["description"]=line

            if line.startswith("Type:"):
                if current_dataset != None:
                    line = line[6:] if line[5:].startswith(" ") else line[5:]
                    current_dataset["type"]=line

            if line.startswith("Format:"):
                if current_dataset != None:
                    line = line[8:] if line[7:].startswith(" ") else line[7:]
                    current_format = line

            if line.startswith("Source:"):
                if current_dataset != None:
                    line = line[8:] if line[7:].startswith(" ") else line[7:]   
                    if line.lower() == "input":                    
                        current_dataset["distribution"] = []
                        current_dataset["distribution"].append({"title":"Origin"})
                        current_dataset["distribution"].append({"title":"Project"})
                    elif line.lower() == "produced":
                        current_dataset["distribution"] = []
                        current_dataset["distribution"].append({"title":"Project"})

        if current_dataset != None:
            if "distribution" not in current_dataset:
                current_dataset["distribution"] = []
                current_dataset["distribution"].append({"title":"Project"})
            else:
                if current_format != None:
                    for ds in current_dataset["distribution"]:
                        ds["format"] = current_format
                    current_format = None
            current_dataset["metadata"] = []
            current_dataset["technical_resource"] = []
            datasets.append(current_dataset)
        
        self.dmp["dmp"]["dataset"]=datasets
        return datasets
    
    def parse_question_1_4(self, text):
        ret_val = {}
        for ds in self.dmp["dmp"]["dataset"]:
            if ds["title"].lower() in text.lower():
                ds["keyword"] = "re-used"
                ret_val[ds["title"]] = "re-used"
            else:
                ds["keyword"] = "generated"
                ret_val[ds["title"]] = "generated"
        return ret_val
    
    def parse_question_1_5(self, text):

        ret_val = {}
        rep = {}
        for ds in self.dmp["dmp"]["dataset"]:
            # check if "input"
            bIsInput = False
            for dist in ds["distribution"]:
                if dist["title"] == "Origin":
                    bIsInput = True
                    break
                    
            
            if bIsInput:
                title = ds["title"].lower()
                rep[title]=";"+title

        rep = dict((re.escape(k), v) for k, v in rep.items()) 
        
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text.lower()).split(";")

        for ds in self.dmp["dmp"]["dataset"]:
            ret_val[ds["title"]] = []
            for dist in ds["distribution"]:
                if dist["title"] == "Origin":
                    for line in text:
                        if line.startswith(ds["title"].lower()):
                            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
                            if len(url) >= 1:
                                url = url[0]
                                if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                                    url = url[:-1]
                                ds["dataset_id"] = {
                                    "dataset_id": url,
                                    "dataset_id_type": "HTTP-URI"
                                }
                                dist["access_url"]=url
                                ret_val[ds["title"]].append({
                                    "dataset_id": url,
                                    "dataset_id_type": "HTTP-URI",
                                    "access_url": url
                                })
                            else:
                                ds["dataset_id"] = {
                                    "dataset_id": ds["title"],
                                    "dataset_id_type": "custom"
                                }
                                ret_val[ds["title"]].append({
                                    "dataset_id": ds["title"],
                                    "dataset_id_type": "custom"
                                })
                            break
                else:
                    if "dataset_id" not in ds:
                        ds["dataset_id"] = {
                            "dataset_id": ds["title"],
                            "dataset_id_type": "custom"
                        }
                        ret_val[ds["title"]].append({
                            "dataset_id": ds["title"],
                            "dataset_id_type": "custom"
                        })
        return ret_val
 
    def parse_question_1_6(self, text):
        ret_val = {}
        order = ['b', 'kb', 'mb', 'gb', 'tb', 'pb']
       
        text = self.__split_text_based_on_title(text)

        for ds in self.dmp["dmp"]["dataset"]:
            for line in text:
                if line.startswith(ds["title"].lower()):
                    regex1  = re.compile(r'(\d+(?:\.\d+)?)\s*([kmgtp]?b)', re.IGNORECASE)
                    regex2 = re.compile(r'(\d+(?:\.\d+)?)',  re.IGNORECASE)
                    size1 = regex1.findall(line)
                    size2 = regex2.findall(line)
                    if len(size1) >= 1:
                        size1 = size1[0]
                        size1 = int(float(size1[0]) * (1024**order.index(size1[1].lower())))
                        
                        for dist in ds["distribution"]:
                            dist["byte_size"]=size1
                        ret_val[ds["title"]] = size1
                    elif len(size2) >= 1:
                        size2 = size2[0]                        
                        for dist in ds["distribution"]:
                            dist["byte_size"]=size2
                        ret_val[ds["title"]] = size2
        return ret_val

    def parse_question_1_7(self, text):
        if "description" in self.dmp["dmp"]:
            text=";Outline the data utility: to whom will it be useful::"+text
            self.dmp["dmp"]["description"] += text
        else:
            text="Outline the data utility: to whom will it be useful::"+text
            self.dmp["dmp"]["description"] = text
        return text
    
    def parse_question_2_1_1(self, text):
        ret_val = []       
        text = self.__split_text_based_on_title(text)

        for ds in self.dmp["dmp"]["dataset"]:
            for line in text:
                if line.startswith(ds["title"].lower()):   
                    
                    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
                    filename = re.findall('[\w\d\-.\/:]+\.\w+', line)
                    if len(url) >= 1:
                        url = url[0] 
                        if url.endswith(".") or url.endswith(",")  or url.endswith(")"):
                            url = url[:-1]
                        ds["metadata"].append({
                            "description":"Dataset Metadata",
                            "language":"en",
                            "metadata_id": {
                                "metadata_id": url,
                                "metadata_id_type": "HTTP-URI"
                            }
                        })
                        ret_val.append({
                            "dataset": ds["title"],
                            "description":"Dataset Metadata",
                            "language":"en",
                            "metadata_id": {
                                "metadata_id": url,
                                "metadata_id_type": "HTTP-URI"
                            }
                        })
                    if len(filename) >= 1:
                        new_names = []
                        for f in filename:
                            if not f.startswith("http"):
                                new_names.append(f)
                        filename = new_names[0] 
                        ds["metadata"].append({
                            "description":"Dataset Metadata",
                            "language":"en",
                            "metadata_id": {
                                "metadata_id": filename,
                                "metadata_id_type": "custom"
                            }
                        })
                        ret_val.append({
                            "dataset": ds["title"],
                            "description":"Dataset Metadata",
                            "language":"en",
                            "metadata_id": {
                                "metadata_id": filename,
                                "metadata_id_type": "custom"
                            }
                        })
        return ret_val
    
    def parse_question_2_1_3(self, text):
        ret_val = []
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        filenames = re.findall('[\w\d\-.\/:]+\.\w+', text)
        
        for url in urls:
            if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                url = url[:-1]
            for ds in self.dmp["dmp"]["dataset"]:
                ds["metadata"].append({
                    "description":"Naming Conventions",
                    "language":"en",
                    "metadata_id": {
                        "metadata_id": url,
                        "metadata_id_type": "HTTP-URI"
                    }
                })
                ret_val.append({
                    "dataset": ds["title"],
                    "description":"Naming Conventions",
                    "language":"en",
                    "metadata_id": {
                        "metadata_id": url,
                        "metadata_id_type": "HTTP-URI"
                    }
                })
            
        for filename in filenames:
            if not filename.startswith("http"):
                for ds in self.dmp["dmp"]["dataset"]:
                    ds["metadata"].append({
                        "description":"Naming Conventions",
                        "language":"en",
                        "metadata_id": {
                            "metadata_id": filename,
                            "metadata_id_type": "custom"
                        }
                    })
                    ret_val.append({
                        "dataset": ds["title"],
                        "description":"Naming Conventions",
                        "language":"en",
                        "metadata_id": {
                            "metadata_id": filename,
                            "metadata_id_type": "custom"
                        }
                    })
        return ret_val
    
    def parse_question_2_1_4(self, text):
        if "description" in self.dmp["dmp"]:
            text=";Outline the approach towards search keyword::"+text
            self.dmp["dmp"]["description"] += text
        else:
            text="Outline the approach towards search keyword ::"+text
            self.dmp["dmp"]["description"] = text
        return text
    
    def parse_question_2_1_5(self, text):
        ret_val = []        
        keywords = ["Endevor", "AccuRev SCM", "ClearCase", "Dimensions CM", "IC Manage", "PTC Integrity", "PVCS", "Rational Team Concert", "SCM Anywhere", "StarTeam", "Subversion", "SVN", "Surround SCM", "Vault", "Perforce Helix Core", "Synergy", "Plastic SCM", "Azure DevOps", "BitKeeper", "Code Co-op", "darcs", "Fossil", "Git", "Mercurial", "Monotone", "Pijul", "GNU Bazaar", "Revision Control System", "Source Code Control System", "Team Foundation Server"]
        text = text.lower()
        for keyword in keywords:
            keyword = keyword.lower()
            if keyword in text:
                for ds in self.dmp["dmp"]["dataset"]:
                    for dist in ds["distribution"]:
                        if dist["title"] == "Project":
                            dist["host"] = {
                                "title": keyword,
                                "supports_versioning": "yes"
                            }
                            ret_val.append({
                                "dataset":ds["title"],
                                "supports_versioning": "yes",
                                "title": keyword
                            })
        return ret_val

    def parse_question_2_1_6(self, text):
        ret_val = []
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        filenames = re.findall('[\w\d\-.\/:]+\.\w+', text)
        
        for url in urls:
            if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                url = url[:-1]
            for ds in self.dmp["dmp"]["dataset"]:
                ds["metadata"].append({
                    "description":"Metadata Creation",
                    "language":"en",
                    "metadata_id": {
                        "metadata_id": url,
                        "metadata_id_type": "HTTP-URI"
                    }
                })
                ret_val.append({
                    "dataset": ds["title"],
                    "description":"Metadata Creation",
                    "language":"en",
                    "metadata_id": {
                        "metadata_id": url,
                        "metadata_id_type": "HTTP-URI"
                    }
                })
            
        for filename in filenames:
            if not filename.startswith("http"):
                for ds in self.dmp["dmp"]["dataset"]:
                    ds["metadata"].append({
                        "description":"Metadata Creation",
                        "language":"en",
                        "metadata_id": {
                            "metadata_id": filename,
                            "metadata_id_type": "custom"
                        }
                    })
                    ret_val.append({
                        "dataset": ds["title"],
                        "description":"Metadata Creation",
                        "language":"en",
                        "metadata_id": {
                            "metadata_id": filename,
                            "metadata_id_type": "custom"
                        }
                    })
        return ret_val
    
    def parse_question_2_2_1(self, text):
        ret_val = {}     
        text = self.__split_text_based_on_title(text)

        for ds in self.dmp["dmp"]["dataset"]:
            for line in text:
                if line.startswith(ds["title"].lower()):   
                    
                    state = "closed"
                    if "open" in line.lower():
                        state = "open"
                    if "closed" in line.lower():
                        state = "closed"
                    
                    for dist in ds["distribution"]:
                        dist["data_access"] = state
                        ret_val[ds["title"]] = state
        return ret_val
    
    def parse_question_2_2_2(self, text):
        ret_val = []
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) >= 1:
            url = urls[0]
            if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                url = url[:-1]
            for ds in self.dmp["dmp"]["dataset"]:
                for dist in ds["distribution"]:
                    if dist["title"] == "Project":
                        dist["access_url"] = url
                        tld = re.findall('[^.]*\.[^.]{2,3}(?:\.[^.]{2,3})?$', url)
                        tld = urlparse(url).netloc
                        dist["host"]["title"] = tld
                        ret_val.append({"access_url": url, "host":{"title":tld}})
        return ret_val
    
    def parse_question_2_2_3(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["technical_resource"].append({
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "software_tools",
                    "technical_resource_id_type": "custom"
                }
            })
            ret_val.append({
                "dataset": ds["title"],
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "software_tools",
                    "technical_resource_id_type": "custom"
                }
            })
            
        return ret_val
    
    def parse_question_2_2_4(self, text):
        return self.parse_question_2_2_2(text)
    
    def parse_question_2_2_5(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["metadata"].append({
                "description": text,
                "metadata_id":{
                    "metadata_id": "restrictions",
                    "metadata_id_type": "custom"
                }
            })
            ret_val.append({
                "dataset": ds["title"],
                "description": text,
                "metadata_id":{
                    "metadata_id": "restrictions",
                    "metadata_id_type": "custom"
                }
            })
            
        return ret_val
    
    def parse_question_2_3_1(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["technical_resource"].append({
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "interoperability_standards",
                    "technical_resource_id_type": "custom"
                }
            })
            ret_val.append({
                "dataset": ds["title"],
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "interoperability_standards",
                    "technical_resource_id_type": "custom"
                }
            })
            
        return ret_val
    
    def parse_question_2_3_2(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["technical_resource"].append({
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "vocabulary_standards",
                    "technical_resource_id_type": "custom"
                }
            })
            ret_val.append({
                "dataset": ds["title"],
                "description": text,
                "technical_resource_id":{
                    "technical_resource_id": "vocabulary_standards",
                    "technical_resource_id_type": "custom"
                }
            })
            
        return ret_val
    
    def parse_question_2_4_1(self, text):
        ret_val = []
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) >= 1:
            url = urls[0]
            if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                url = url[:-1]
            for ds in self.dmp["dmp"]["dataset"]:
                for dist in ds["distribution"]:
                    if dist["title"] == "Project":
                        dist["host"]["license"] = {
                            "license_ref": url
                        }
                        ret_val.append({
                            "dataset": ds["title"],
                            "license_ref": url
                        })
        return ret_val
    
    def parse_question_2_4_2(self, text):
        ret_val = []        
        dates = list(datefinder.find_dates(text))
        if len(dates) >= 1:
            date = dates[0]
            for ds in self.dmp["dmp"]["dataset"]:
                for dist in ds["distribution"]:
                    if dist["title"] == "Project":
                        if "license" in dist["host"]:
                            dist["host"]["license"]["start_date"] = date.strftime("%Y-%d-%m")
                        else:                          
                            dist["host"]["license"] = {
                                "start_date": date.strftime("%d-%m-%Y")
                            }
                        ret_val.append({
                            "dataset": ds["title"],
                            "start_date": date.strftime("%d-%m-%Y")
                        })
        else:
            for ds in self.dmp["dmp"]["dataset"]:
                for dist in ds["distribution"]:
                    if dist["title"] == "Project":
                        if "license" in dist["host"]:
                            dist["host"]["license"]["start_date"] = self.dmp["dmp"]["created"]
                        else:                          
                            dist["host"]["license"] = {
                                "start_date": self.dmp["dmp"]["created"]
                            }
                        ret_val.append({
                            "dataset": ds["title"],
                            "start_date": self.dmp["dmp"]["created"]
                        })  
        return ret_val
    
    def parse_question_2_4_3(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["metadata"].append({
                "description": text,
                "metadata_id":{
                    "metadata_id": "third_party_usability",
                    "metadata_id_type": "custom"
                }
            })
            ret_val.append({
                "dataset": ds["title"],
                "description": text,
                "metadata_id":{
                    "metadata_id": "third_party_usability",
                    "metadata_id_type": "custom"
                }
            })
            
        return ret_val 
    
    def parse_question_2_4_4(self, text):
        ret_val = {}
        for ds in self.dmp["dmp"]["dataset"]:
            ds["data_quality_assurance"] = text
            ret_val[ds["title"]] = text
        return ret_val
    
    def parse_question_2_4_5(self, text):
        ret_val = []        
        dates = list(datefinder.find_dates(text))
        if len(dates) >= 1:
            date = dates[0]
            for ds in self.dmp["dmp"]["dataset"]:
                for dist in ds["distribution"]:
                    if dist["title"] == "Project":
                        if "license" in dist["host"]:
                            dist["available_till"] = date.strftime("%Y-%d-%m")
                        ret_val.append({
                            "dataset": ds["title"],
                            "available_till": date.strftime("%d-%m-%Y")
                        })
        return ret_val
    
    def parse_question_3_1(self, text):
        cost = {
            "title": "Costs for making your data FAIR",
            "description": text
        }
        prices = re.findall('(\$|€|EUR|USD)(\d*[.|,]*\d*)', text)        
        if len(prices) >= 1:
            price = prices[0]
            code = price[0]
            if code.lower().startswith("eur"):
                cost["currency_code"] = "EUR"
                cost["value"] = price[1]
            if code.lower().startswith("usd"):
                cost["currency_code"] = "USD"
                cost["value"] = price[1]
            if code.lower().startswith("$"):
                cost["currency_code"] = "USD"
                cost["value"] = price[1]
            if code.lower().startswith("€"):
                cost["currency_code"] = "EUR"
                cost["value"] = price[1]
            
        self.dmp["dmp"]["cost"] = [cost]
        return cost
    
    def parse_question_3_2(self, text):
        dmp_staff = []
        
        lines = text.split("\n")        
        current_staff = None
        for line in lines:
            # is URL?
            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
            if len(url) >= 1:
                current_staff["staff_id"] = {
                    "staff_id":url[0],
                    "staff_id_type": "HTTP-ORCID"
                }
                continue
                
            # is EMAIL?
            email = re.findall(r'[\w\.]+\@[\w]+(?:\.[\w]{3}|\.[\w]{2}\.[\w]{2})\b', line)
            if len(email) >= 1:
                current_staff["mbox"] = email[0]
                continue
                
            # else new staff
            if current_staff != None:
                dmp_staff.append(current_staff)
            current_staff = {}    
            current_staff["name"] = line
            
        if current_staff != None:
            dmp_staff.append(current_staff)
        
        self.dmp["dmp"]["dm_staff"] = dmp_staff
        return dmp_staff
    
    def parse_question_3_3(self, text):
        ret_val = {}
        for ds in self.dmp["dmp"]["dataset"]:
            ds["preservation_statement"] = text
            ret_val[ds["title"]] = text
        return ret_val

    def parse_question_4_1(self, text):
        ret_val = []
        for ds in self.dmp["dmp"]["dataset"]:
            ds["security_and_privacy"] = [{
                "title": "Data Security",
                "text": text
            }]
            ret_val.append({
                "dataset": ds["title"],
                "title": "Data Security",
                "text": text
            })
        return ret_val
    
    def parse_question_5_1(self, text):
        ret_val = {}
        
        self.dmp["dmp"]["ethical_issues_description"] = text
        ret_val["ethical_issues_description"] = text
        
        self.dmp["dmp"]["ethical_issues_exist"] = "no"
        ret_val["ethical_issues_exist"] = "no"
        
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(url)>=1:
            url = url[0]
            if url.endswith(".") or url.endswith(",") or url.endswith(")"):
                url = url[:-1]
            self.dmp["dmp"]["ethical_issues_report"] = url
            ret_val["ethical_issues_report"] = url
            
            self.dmp["dmp"]["ethical_issues_exist"] = "yes"
            ret_val["ethical_issues_exist"] = "yes"
            
        return ret_val
    
    def parse_question_6_1(self, text):
        q = "Refer to other national/funder/sectorial/departmental procedures for data management that you are using (if any)"
        if "description" in self.dmp["dmp"]["project"]:
            text=";"+q+"::"+text
            self.dmp["dmp"]["project"]["description"] += text
        else:
            text=q+"::"+text
            self.dmp["dmp"]["project"]["description"] = text
        return text
    
    def generate(self):
        return json.dumps(self.dmp, indent=2, sort_keys=False)