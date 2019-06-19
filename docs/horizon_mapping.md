## Mapping - Horzion2020

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

#### Question 1.1: State the purpose of the data collection/generation
This is general information about the project and data and should therefore be mapped to **dmp:project:description**. No additional parsing is needed.

#### Question 1.2: Explain the relation to the objectives of the project
This is general information about the relation between the data and the DMP to the project and should therefore be mapped to **dmp:description**. No additional parsing is needed.

#### Question 1.3: Specify the types and formats of data generated/collected
*Assumption: In order to corretly identify the different data/datsets used in the project/described in the DMP we need at least once a somewhat structured input of information.*

This text is expected to have the following structure for each dataset:

Title: \<title\> \
Description: \<description\> \
Type: \<Type\> \
Format: \<Format\> \
Source: ["input", "produced"]

a possible sample could look like this:

Title: Ehescheidungen (Statistik Austria) \
Description: Divorce statistic of austria \
Type: Dataset \
Format: csv \
Source: input

For each dataset the mapping is as follows: \
* a new **dataset** with **dmp:dataset:title** \<title\> is created
* \<description\> is mapped to **dmp:dataset:description**
* \<type\> is mapped to **dmp:dataset:typ**
* a new **distribution** is added to the **dmp:dataset** where the **dmp:dataset:distribution:title** is set to "Project" if \<source\> equals "produced" or missing. If \<source\> equals "input" two **distribution** items are added to the **dmp:dataset** where one has the title "Project" and one has the title "Origin".
* \<format\> is mapped to **dmp:dataset:distribution:format**

#### Question 1.4: Specify if existing data is being re-used (if any) 
*Assumption: If the title of a dataset is found in this answer, it is assumed that the data is being reused*

We could not find a matching field in the ontology so we decided to add it to the keywords of the dataset. For every **dmp:dataset** the first **keyword** is either set to "generated" or "re-used" (if the title was mentioned in the text).

#### Question 1.5: Specify the origin of the data

We look for occurrences of previously defined dataset titles (only input datasets are considered since the origin of produced datasets is the project) in the text. The string between two such titles is searched for a URL. If a URL is found the following mapping applies:
* the URL is mapped to **dmp:dataset:dataset_id:dataset_id**
* **dmp:dataset:dataset_id:dataset_id_type** is set to  "HTTP-URI"
* the URL is mapped to  **dmp:dataset:distribution:access_url** (where **dmp:dataset:distribution:title** equals "Origin")

if no URL was found, the title was not in the text or it is a produced dataset the following mapping is applied:
* the title of the dataset is mapped to **dmp:dataset:dataset_id:dataset_id**
* **dmp:dataset:dataset_id:dataset_id_type** is set to  "custom"

#### Question 1.6: State the expected size of the data (if known) 
*Assumption: if no size information was given (only a number without e.g. mb, GB, etc..) it is assumed that the number is the file-size in bytes.*

We use the same parsing method as for question 1.5 but instead of looking for URLs we are now looking for file sizes e.g.:
* 15KB
* 30.5 Mb
* 900
* 1.4gb

Supported file sizes for conversion: b, kb, mb, gb, tb, pb

If a file size for a dataset is found it is mapped to **dmp:dataset:distribution:byte_size** for all distributions. It is also converted into bytes.


#### Question 1.7: Outline the data utility: to whom will it be useful 
We could not think of any structured data/information that would map to fields of the ontology. Therefore the text is append to **dmp:project:description**.

#### Question 2.1.1: Outline the discoverability of data (metadata provision)
We use the same parsing method as for question 1.5 and 1.6. We are looking for file names and URLs. If one of those is found we create an entry for the **dmp:dataset:metadata** field and apply following mapping:
* **dmp:dataset:metadata:description** is set to "Dataset Metadata"
* **dmp:dataset:metadata:language** is set to "en"

if a filename was found we continue with:
* **dmp:dataset:metadata:metadata_id:metadata_id** is set to the filename
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "custom"

if a URL was found we continue with:
* **dmp:dataset:metadata:metadata_id:metadata_id** is set to the URL
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "HTTP-URI"

multiple entries for "Dataset Metadata" might exist (e.g. one referring to a file and one referring to a URL)

#### Question 2.1.2: Outline the identifiability of data and refer to standard identification mechanism. Do you make use of persistent and unique identifiers such as Digital Object Identifiers? 
*Assumption: We assume that there is only one unique identifier per project*
Generally we would parse the text and look for a URL and set it as **dmp:dmp_id**. However we already have a mapping for **dmp:dmp_id** from the DMP metadata and therefore we can skip processing this question.

#### Question 2.1.3 Outline naming conventions used 
*Assumption: We assume that the whole project follows the same naming conventions.*

We simply parse the text for filenames and URLs and apply for each found "naming convention" following mapping: 
* **dmp:dataset:metadata:description** is set to "Naming Conventions"
* **dmp:dataset:metadata:language** is set to "en"
* **dmp:dataset:metadata:metadata_id:metadata_id** is mapped to the URL or filename
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "HTTP-URI" or "custom"

#### Question 2.1.4:  Outline the approach towards search keyword 
Neither of us had this question filled out. We also couldn't come up with an answer that contains structured data mappable to the RDA-DMP-Common-Standards ontology. We decided to append it to **dmp:description** if the question is answered.

#### Question 2.1.5: Outline the approach for clear versioning 
*Assumption: We assume that versioning applies to the whole project and not to each dataset individually.*

The only field on the RDA-DMP-Common-Standards that made sense for us to map this to is **dmp:dataset:distribution:host:support_versioning**. However we found it hard to find out from plain text if versioning is supported. We decided to define a list of keywords (version control systems) that we are looking for in the text. 

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

#### Question 2.1.6: Specify standards for metadata creation (if any). If there are no standards in your discipline describe what metadata will be created and how 
Similar to question 2.1.3 we are looking for URLs and filenames in the answer. If a "standard" is found following mapping is applied: 
* **dmp:dataset:metadata:description** is set to "Metadata Creation"
* **dmp:dataset:metadata:language** is set to "en"
* **dmp:dataset:metadata:metadata_id:metadata_id** is mapped to the URL or filename
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "HTTP-URI" or "custom"

#### Question 2.2.1: Specify which data will be made openly available? If some data is kept closed provide rationale for doing so
*Assumption: By default we assume that datasets are not openly available*

We look for occurrences of previously defined dataset titles in the text. The string between two such titles is searched for the keywords "open" and "closed". If one of the keywords is found, following mapping applies:
* **dmp:dataset:distribution:data_access** is set to the keyword

If both or no keyword was found, **dmp:dataset:distribution:data_access** is set to "closed".

#### Question 2.2.2: Specify how the data will be made available
*Assumption: The project and data are hosted/stored/distributed at/from the same place and share the same URL*

The text is parsed for an URL and if found for each **dmp:dataset:distribution** where the **dmp:dataset:distribution:title** equals "Project" the following mapping is applied:
* **dmp:dataset:distribution:access_url** is set to the URL
* **dmp:dataset:distribution:host:title** is changed to the top level domain name of the url 

#### Question 2.2.3: Specify what methods or software tools are needed to access the data? Is documentation about the software needed to access the data included? Is it possible to include the relevant software (e.g. in open source code)?
We found that the best mapping for this question would be **dmp:dataset:technical_resource**. However, extracting meaningfull parts for each dataset separatelty is to hard of a problem for this exercise and therefore we decided to apply the same mapping for each **dmp:dataset** which is:
* **dmp:dataset:technical_resource:description** is mapped to the answer text
* **dmp:dataset:technical_resource:resource_id:resource_id** is set "software_tools"
* **dmp:dataset:technical_resource:resource_id:resource_id_type** is set to "custom" 

This mapping allows parsers to look for a **dmp:dataset:technical_resource:resource_idresource_id_type** equal to "software_tools" in order to retrieve the relevant information.

#### Question 2.2.4: Specify where the data and associated metadata, documentation and code are deposited 
For us the answer to this question should be very similar to Question 2.2.2. We therefore apply the same mapping. This is only a safeguard function if anyone did not provide a URL in Question 2.2.2.

#### Question 2.2.5: Specify how access will be provided in case there are any restrictions
Type of data access and where it is located is already covered by previous questions. For restrictions that might apply we found no field to map to and decided to go for the same approach as in question 2.2.3 and apply following mapping: 
* **dmp:dataset:metadata:description** is mapped to the answer text
* **dmp:dataset:metadata:metadata_id:metadata_id** is set "restirctions"
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "custom" 

This mapping allows parsers to look for a **dmp:dataset:metadata:metadata_id:metadata_id** equal to "restrictions" in order to retrieve the relevant information.

#### Question 2.3.1: Assess the interoperability of your data. Specify what data and metadata vocabularies, standards or methodologies you will follow to facilitate interoperability. 
For interoperability standards, we found no field to map to and decided to go for the same approach as in question 2.2.3 and apply following mapping: 
* **dmp:dataset:technical_resource:description** is mapped to the answer text
* **dmp:dataset:technical_resource:resource_id:resource_id** is set "interoperability_standards"
* **dmp:dataset:technical_resource:resource_id:resource_id_type** is set to "custom" 

This mapping allows parsers to look for a **dmp:dataset:technical_resource:resource_id:resource_id** equal to "interoperability_standards" in order to retrieve the relevant information.

#### Question 2.3.2: Specify whether you will be using standard vocabulary for all data types present in your data set, to allow inter-disciplinary interoperability? If not, will you provide mapping to more commonly used ontologies?
For vocabulary standards, we found no field to map to and decided to go for the same approach as in question 2.2.3 and apply following mapping: 
* **dmp:dataset:technical_resource:description** is mapped to the answer text
* **dmp:dataset:technical_resource:resource_id:resource_id** is set "vocabulary_standards"
* **dmp:dataset:technical_resource:resource_id:resource_id_type** is set to "custom" 

This mapping allows parsers to look for a **dmp:dataset:technical_resource:resource_id:resource_id** equal to "vocabulary_standards" in order to retrieve the relevant information.

#### Question 2.4.1:  Specify how the data will be licenced to permit the widest reuse possible 
*Assumption: The license is specified by its unique identifier, where we made the global assumption that it has to be a URL (this is the case for most licenses anyway)*

*Assumption: The same license applies for all the data in the project.*

The answer text is parsed for an URL and if found following mapping is applied:
* **dmp:dataset:distribution:license:license_ref** is mapped to the URL

This mapping is applied only if **dmp:dataset:distribution:title** equals "Project".

#### Question 2.4.2: Specify when the data will be made available for re-use. If applicable, specify why and for what period a data embargo is needed 
*Assumption: We assume that all the datasets are made available at the same time (e.g. the time the project gets published)*

We parse the text for a date, if a date is found following mapping is applied:
**dmp:dataset:distribution:license:start_date** is mapped to the date

If no date was found, **dmp:dataset:distribution:license:start_date** is set to the creation date of the dmp.

The mapping is only applied where **dmp:dataset:distribution:title** equals "Project".

#### Question 2.4.3: Specify whether the data produced and/or used in the project is useable by third parties, in particular after the end of the project? If the re-use of some data is restricted, explain why
For third-party access we found no field to map to and decided to go for the same approach as in question 2.2.5 and apply following mapping: 
* **dmp:dataset:metadata:description** is mapped to the answer text
* **dmp:dataset:metadata:metadata_id:metadata_id** is set "third_party_usability"
* **dmp:dataset:metadata:metadata_id:metadata_id_type** is set to "custom" 

This mapping allows parsers to look for a **dmp:dataset:metadata:metadata_id:metadata_id** equal to "third_party_usability" in order to retrieve the relevant information.

#### Question 2.4.4: Describe data quality assurance processes 
*Assumption: We assume that the same quality assurance processes is applied to all datasets in the project*

The answer text is mapped to **dmp:dataset:data_quality_assurance**

#### Question 2.4.5:Specify the length of time for which the data will remain re-usable 
*Assumption: We assume that all the datasets are available for the same period*

We parse the text for a date, if a date is found following mapping is applied:
* **dmp:dataset:distribution:available_till** is mapped to the date.

The mapping is only applied where **dmp:dataset:distribution:title** equals "Project".

#### Question 3.1: Estimate the costs for making your data FAIR. Describe how you intend to cover these costs
*Assumption: Prices are defined in either Euro or USD with EUR, USD, $ or $ as currency indicator. The currency indicator is the first part of the price e.g. $100 or EUR100.000*

A **dmp:cost** entry is added to the **dmp** with following mapping:
* **dmp:cost:title** is set to "Costs for making your data FAIR"
* **dmp:cost:title** is mapped to the text

Additionally we parse the text for price values and if found the following mapping is added:
* **dmp:cost:currency_code** is mapped the found currency indicator
* **dmp:cost:value** is mapped to found amount

#### Question 3.2: Clearly identify responsibilities for data management in your project 
*Assumption: In order to reliably parse the information of this answer, each information has to be on its own line e.g.:
Martin Pichler
mpichler.dev@gmail.com
https://orcid.org/0000-0001-5305-9063*

*Assumption: Person IDs are always valid ORCID IDs*

We parse the text line by line and look for URLs and Emails. If a parsed line is not an Email or a URL in is interpreted as the name of a person indicating the start of a new **dm_staff** entry. For each person following mapping is applied:
* **dmp:dm_staff:name** is mapped the name
* **dmp:dm_staff:contributor_type** is set to "Data Manager"
* **dmp:dm_staff:mbox** is mapped to Email
* **dmp:dm_staff:staff_id:staff_id** is mapped to the URL
* **dmp:dm_staff:staff_id:staff_id_type** is set to "HTTP-ORCID"

#### Question 3.3: Describe costs and potential value of long term preservation 
*Assumption: We assume that the same preservation processes is applied to all datasets in the project*

The answer text is mapped to **dmp:dataset:preservation_statement**

#### Question 4.1: Address data recovery as well as secure storage and transfer of sensitive data
The answer text of this question is added as a new entry to **security_and_privacy** with following mapping:
* **dmp:dataset:security_and_privacy:title** = "Data Security"
* **dmp:dataset:security_and_privacy:description** = Text

#### Question 5.1: To be covered in the context of the ethics review, ethics section of DoA and ethics deliverables. Include references and related technical aspects if not covered by the former 
*Assumption: It is assumed that no ethical issues exist by default*

We parse the text and apply following mapping:
* **dmp:ethical_issues_description** is mapped to the text

Additionally we parse the text for an URL. If an URL is found it is assumed to link to an ethical issues report and following mapping is applied:
* **dmp:ethical_issues_report** is mapped to URL
* **dmp:ethical_issues_exist** is set to "yes"

#### Question 6.1:  Refer to other national/funder/sectorial/departmental procedures for data management that you are using (if any) 
For the last question we could not think of any structured data to extract and we decided to append it to **dmp:project:description**