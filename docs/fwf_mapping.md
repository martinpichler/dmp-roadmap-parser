## FWF Mapping

### General Assumptions and Schema Design

1. We assume all unique identifiers (identifierType - http://www.sysresearch.org/rda-common-dmp#identifierType) that occure in the DMP are in the form of an URL. This assumption is made to speed up implementation of the parser and can later be adapted to recognize other identifiers.
2. Plain text answers (e.g. text in description) of different questions are separated by ";" and have the form **\<question\>::\<answer\>**
3. In our definition of the RDA-DMP-Common-Standard a dataset can have two distribution items. If the title of the distribution item is set to "Origin" it indicates that this distribution item contains information about the original source/location of input data. If the title is set to "Project" it indicates that this distribution item contains information about the source/location of the project.
4. Keywords are comma (",") separated strings.
5. We assume the DMP is written in English

#### DMP Data
*Assumption: we expect that the ID of the DMP is a DOI in URL form.*

DMP metadata is mapped as follows:
* Project title is mapped to **dmp:title**
* Project abstract is mapped to **dmp:description**
* Creation date is mapped to **dmp:created**
* Modification date is mapped to **dmp::modified**
* ID is mapped to **dmp:dmp_id:dmp_id** and **dmp:dmp_id:dmp_id_type** is set to "HTTP-DOI"
* Principle investigator name is mapped to **dmp:contact:name**
* Principle investigator email is mapped to **dmp:contact:mail**
* Principle investigator ORCID is mapped to **dmp:contact:contact_id:contact_id** and **dmp:contact:contact_id:contact_id_type** is set to "HTTP-ORCID"

#### Question 1.1: Beschreibung der Daten
*Assumption: In order to corretly identify the different data/datsets used in the project/described in the DMP we need at least once a somewhat structured input of information.*

*Assumption: if no size information was given (only a number without e.g. mb, GB, etc..) it is assumed that the number is the file-size in bytes.*

This text is expected to have the following structure for each dataset:

Title: \<title\> \
Description: \<description\> \
Type: \<Type\> \
Format: \<Format\> \
Source: ["input", "produced"]
Size: \<Size\>

a possible sample could look like this:

Title: Ehescheidungen (Statistik Austria) \
Description: Divorce statistic of austria \
Type: Dataset \
Format: csv \
Source: input
Size: 15kb

For each dataset the mapping is as follows: \
* a new **dataset** with **dmp:dataset:title** \<title\> is created
* \<description\> is mapped to **dmp:dataset:description**
* \<type\> is mapped to **dmp:dataset:typ**
* a new **distribution** is added to the **dmp:dataset** where the **dmp:dataset:distribution:title** is set to "Project" if \<source\> equals "produced" or missing. If \<source\> equals "input" two **distribution** items are added to the **dmp:dataset** where one has the title "Project" and one has the title "Origin".
* \<format\> is mapped to **dmp:dataset:distribution:format**
* \<Size\> is mapped to **dmp:dataset:distribution:byte_size**

Additionally to incorporate versioning information we decided to define a list of keywords (version control systems) that we are looking for in the text. 

If a match was found following mapping is applied to each **dmp:datasets:distribution** where the title equals "Project"  (since we only want to apply the versioning info to the data hosted/provided by the project):
* **dmp:dataset:distribution:host:support_versioning** is set to "yes"
* **dmp:dataset:distribution:host:title** is set to the keyword. 

The following list of version control systems (keywords are supported):
* Endevor
* AccuRev SCM
* ClearCase
* Dimensions CM
* IC Manage
* PTC Integrity
* PVCS
* Rational Team Concert
* SCM Anywhere
* StarTeam
* Subversion
* SVN
* Surround SCM
* Vault
* Perforce Helix Core
* Synergy
* Plastic SCM
* Azure DevOps
* BitKeeper
* Code Co-op
* darcs
* Fossil
* Git
* Mercurial
* Monotone
* Pijul
* GNU Bazaar
* Revision Control System
* Source Code Control System
* Team Foundation Server

The list was created by looking at the actively developed version control systems at (https://en.wikipedia.org/wiki/Comparison_of_version-control_software) and by making personal additions.

#### Question 2.1: Metadaten Standards
We look for occurrences of previously defined dataset titles in the text. The string between two such titles is searched for file names and URLs. If one of those is found we create an entry for the **dmp:dataset:metadata** field and apply following mapping:
* **dmp:dataset:metadata:description** is set to "Dataset Metadata"
* **dmp:dataset:metadata:language** is set to "en"
* 
#### Question 2.2: Dokumentation der Daten
*Assumption: The project and data are hosted/stored/distributed at/from the same place and share the same URL*

The text is parsed for an URL and if found for each **dmp:dataset:distribution** where the **dmp:dataset:distribution:title** equals "Project" the following mapping is applied:
* **dmp:dataset:distribution:access_url** is set to the URL
* **dmp:dataset:distribution:host:title** is changed to the top level domain name of the url 
  
#### Question 2.3: Kontrolle der Datenqualität
*Assumption: We assume that the same quality assurance processes is applied to all datasets in the project*

The answer text is mapped to **dmp:dataset:data_quality_assurance**

#### Question 3.1: Datennutzungsstrategie
We look for occurrences of previously defined dataset titles (only input datasets are considered since the origin of produced datasets is the project) in the text. The string between two such titles is searched for a URL. If a URL is found the following mapping applies:
* the URL is mapped to **dmp:dataset:dataset_id:dataset_id**
* **dmp:dataset:dataset_id:dataset_id_type** is set to  "HTTP-URI"
* the URL is mapped to  **dmp:dataset:distribution:access_url** (where **dmp:dataset:distribution:title** equals "Origin")

if no URL was found, the title was not in the text or it is a produced dataset the following mapping is applied:
* the title of the dataset is mapped to **dmp:dataset:dataset_id:dataset_id**
* **dmp:dataset:dataset_id:dataset_id_type** is set to  "custom"

#### Question 3.2: Datenspeicherungsstrategie
The answer text of this question is added as a new entry to **security_and_privacy** with following mapping:
* **dmp:dataset:security_and_privacy:title** = "Legal Aspects"
* **dmp:dataset:security_and_privacy:description** = Text

#### Question 4.1: Rechtliche Aspekte
The answer text of this question is added as a new entry to **security_and_privacy** with following mapping:
* **dmp:dataset:security_and_privacy:title** = "Legal Aspects"
* **dmp:dataset:security_and_privacy:description** = Text

#### Question 4.2: Ethische Aspekte
*Assumption: It is assumed that no ethical issues exist by default*

We parse the text and apply following mapping:
* **dmp:ethical_issues_description** is mapped to the text

Additionally we parse the text for an URL. If an URL is found it is assumed to link to an ethical issues report and following mapping is applied:
* **dmp:ethical_issues_report** is mapped to URL
* **dmp:ethical_issues_exist** is set to "yes"
