# DMP-Roadmap Parser
DMP-Roadmap parser is a tool to create machine actionable DMPs from a *[dmp-roadmap](https://github.com/DMPRoadmap/roadmap)* instance. The tool was created for a university project and is not meant for use in production. The machine actionable DMPs are stored in .json format and follows the [DMP Common Standards WG](https://github.com/DMPRoadmap/roadmap) ontology for creating machine actionable DMPS.

## Mapping
Currently only the [Horizon2020](http://ec.europa.eu/research/participants/docs/h2020-funding-guide/cross-cutting-issues/open-access-data-management/data-management_en.htm) and the [FWF Der Wissenschaftsfond](https://www.fwf.ac.at/de/forschungsfoerderung/open-access-policy/forschungsdatenmanagement/) DMP templates are supported. A detailed description of the mapping for both templates can be found here:
* **[Horizon2020](docs/horizon_mapping.md)**
* **[FWF](docs/fwf_mapping.md)**
## Technical Guides
The following files contain information on how to setup *dmp-roadmap* and how to use dmp-roadmap parser to generate machine actionable DMPs:
* **[DMP-Roadmap setup](docs/dmp-roadmap_setup.md)**
* **[DMP-Roadmap parser usage](docs/dmp-roadmap-parser_usage.md)**

## Examples
We have included some example DMPs and the corresponding machine actionable DMPs for you to see the results.
* */examples/dmps* - contains DMPs exported from *dmp-roadmap* as PDFs
* */examples/ma-dmps* - contains the matching machine actionable DMPs