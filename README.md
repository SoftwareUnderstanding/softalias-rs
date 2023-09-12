# softalias-rs

Softalias-rs is a service that uses [Softalias-KG](https://github.com/SoftwareUnderstanding/softalias-kg) as a reconciliation service for similar tool mentions, which we have integrated with the Named Entity Recognition (NER) model [Softcite](http://dx.doi.org/10.1145/3459637.3481936)  trained in the biomedical domain to extract software mentions. 

**Demo:** See a [demo] (https://softalias-rs.linkeddata.es/).

**Authors:** Daniel Garijo and Esteban Gonzalez

## Requirements:
Softalias-rs has been tested in Unix operating systems.

- Python 3.8 - 3.11
- PIP
- Streamlit 1.24
- Softcite service 0.7.1.

Make sure you have deployed the Softalias-KG in a SPARQL endpoint.

To install streamlit, follow these [instructions](https://docs.streamlit.io/library/get-started/installation)

To install a service of softcite, follow these [instructions](https://github.com/softcite/software-mentions). An open softcite service can be found [here](https://cloud.science-miner.com/software/)

## Install from GitHub

To run softalias-rs, please follow the next steps:

Clone this GitHub repository

```
git clone https://github.com/SoftwareUnderstanding/softalias-rs.git
```

Install the python libraries required.

```
cd softalias-rs
pip install -e .
```
To run the service, execute

```
streamlit run app.py
```

The service will be available in the port 8501.

## Install through Docker

We provide a docker image for the service.

First, you have to build the docker image

```bash
docker build -t softalias-rs .
```

Then, you can run the service with the command

```bash
docker run -d softalias-rs
```
## Contribute

If you want to contribute with a pull request, please do so by submitting it to the dev branch.



