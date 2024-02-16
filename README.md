# SSRQ Retro Lab

This repository contains code (python scripts as well as jupyter notebooks) and data of retrodigitized units of the collection of Swiss Law Sources (SLS). The data is used for various experiments to evaluate the quality of the digitzation process, to improve the quality of the OCR results and to develop a workflow for the retrodigitization of the SLS collection. Furthermore, it shows possible ways for further usage of the data by using advanced methods like topic modeling or named entity recognition.

## Table of Contents

- [SSRQ Retro Lab](#ssrq-retro-lab)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
    - [Swiss Law Sources](#swiss-law-sources)
    - [Idea of the 'Retro Lab'](#idea-of-the-retro-lab)
  - [Data and Code](#data-and-code)
    - [Data](#data)
    - [Code](#code)
  - [Experiments](#experiments)
    - [v1 of the experiment](#v1-of-the-experiment)
    - [v2 of the experiments](#v2-of-the-experiments)
  - [Authors](#authors)
  - [References](#references)
  - [Tools used](#tools-used)


## Background

### Swiss Law Sources

The Swiss law Sources were established at the end of the 19th century by the Swiss Lawyers' Association with the aim of making sources of the legal history of Switzerland accessible to an interested public. The collection of legal sources is nowadays supported by a foundation established in 1980. Part of this foundation is the ongoing research project under the direction of Pascale Sutter. About 15 years ago, the Foundation decided to start digitising the collection of Swiss law sources. The result of this process is the online platform called ["SSRQ Online"](https://www.ssrq-sds-fds.ch/online/cantons.html), which makes all scanned books as PDFs available to the public. The PDFs have been further processed by OCR software, but no correction or any other post-processing (e.g. annotation of named entities) has been done so far. The PDFs are just the starting point for a long journey of further processing and analysis.

### Idea of the 'Retro Lab'

The idea of the 'Retro Lab' is to use the digitized volumes of the SLS collection as a testbed for various experiments. Different methods and tools are used to evaluate the quality of the digitization process, to improve the quality of the OCR results and to develop a workflow for the retrodigitization of the SLS collection. A special focus is on the usage of **generative AI** models like GPT-3.5/4 to create an advanced processing pipeline, where most of the hard work is done by the AI.

## Data and Code

### Data

The data is stored in the folder `data`. It contains the following subfolders:

- [export](./data/export): Contains a ground truth transcription of 53 pages from two volumes. This transcription was created in transkribus and exported as a txt file.
- [ZG](./data/ZG): Contains the OCR results of the volume "ZG" (Zug) as a PDF file. The OCR results were created by the OCR software Abbyy Finereader. Furthermore it contains training and validation data as txt- and json-files.

### Code

The code of the project is divided into two parts:

1. Utility code, organized in python modules (everything beneath `src`)
2. Analysis code, organized in jupyter notebooks (everything beneath `notebooks`)

All dependencies are listed in the [pyproject.toml](./pyproject.toml) file. The code is written for python >= 3.11. The management of virtual environments is done with [hatch](https://github.com/pypa/hatch). To create a new virtual environment, run `hatch env create` in the root directory of the project. To activate the environment, run `hatch env shell`. The environment will have all dependencies installed.

Note: You will need a valid API key for the OpenAI API to run the notebooks.

## Experiments

### v1 of the experiment

For the first iteration of the experiments take a look at the [`v1`-branch](https://github.com/SSRQ-SDS-FDS/ssrq-retro-lab/tree/v1-ocr-and-classification).

### v2 of the experiments

The second iteration of the experiments tries to use a slightly different approach. Instead of just relying on the extracted plain text and trying to use a Large Language Model for further processing (like recognition of different documents) a mixed approach is used, which combines 'classical' methods with the usage of a Large Language Model. Therefore, a [pipeline](./src/ssrq_retro_lab/pipeline/chain.py) is created, which uses a combination of Python scripts and calls a LLM just for the parts, where it is really needed. The pipeline is shown in the following figure:

![Pipeline](./static/pipeline.png)

Each component is validated by a simple set of tests, which are located in the [tests](./tests) folder.

*No Langchain – why?* – [Langchain](https://www.langchain.com/) is a powerful, but also complex, framework. Most of it's features are not needed for the experiments. Instead a custom pipeline (chain) is created, which is tailored to the needs of the experiments.

## Authors

[Bastian Politycki](https://github.com/Bpolitycki) – University of St. Gallen / Swiss Law Sources

## References

- Ekin, Sabit. „Prompt Engineering For ChatGPT: A Quick Guide To Techniques, Tips, And Best Practices“. Preprint, 29. April 2023. [https://doi.org/10.36227/techrxiv.22683919.v1](https://doi.org/10.36227/techrxiv.22683919.v1).
- González-Gallardo, Carlos-Emiliano, Emanuela Boros, Nancy Girdhar, Ahmed Hamdi, Jose G. Moreno, und Antoine Doucet. „Yes but.. Can ChatGPT Identify Entities in Historical Documents?“ arXiv, 30. März 2023. [https://doi.org/10.48550/arXiv.2303.17322](https://doi.org/10.48550/arXiv.2303.17322).
- Liu, Yuliang, Zhang Li, Hongliang Li, Wenwen Yu, Yang Liu, Biao Yang, Mingxin Huang, u. a. „On the Hidden Mystery of OCR in Large Multimodal Models“. arXiv, 18. Juni 2023. [https://doi.org/10.48550/arXiv.2305.07895](https://doi.org/10.48550/arXiv.2305.07895).
- - Møller, Anders Giovanni, Jacob Aarup Dalsgaard, Arianna Pera, und Luca Maria Aiello. „Is a Prompt and a Few Samples All You Need? Using GPT-4 for Data Augmentation in Low-Resource Classification Tasks“. arXiv, 26. April 2023. [http://arxiv.org/abs/2304.13861](http://arxiv.org/abs/2304.13861).
- Pollin, C. (2023). Workshopreihe "Angewandte Generative KI in den (digitalen) Geisteswissenschaften" (v1.0.0). Zenodo. [https://doi.org/10.5281/zenodo.10065626](https://doi.org/10.5281/zenodo.10065626).
- Rockenberger, Annika. „Automated Text Recognition with ChatGPT 4“. Annika Rockenberger (blog), 19. Oktober 2023. [https://www.annikarockenberger.com/2023-10-19/automated-text-recognition-with-chatgpt-4/](https://www.annikarockenberger.com/2023-10-19/automated-text-recognition-with-chatgpt-4/).
- Zhou, Wenxuan, Sheng Zhang, Yu Gu, Muhao Chen, und Hoifung Poon. „UniversalNER: Targeted Distillation from Large Language Models for Open Named Entity Recognition“, 2023. [https://doi.org/10.48550/ARXIV.2308.03279](https://doi.org/10.48550/ARXIV.2308.03279).

## Tools used

- [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) - for creating programmable prompt templates
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [parsel](https://parsel.readthedocs.io/en/latest/)
- [pytest](https://docs.pytest.org/en/8.0.x/)
- [spacy](https://spacy.io/)

For a complete list see [pyproject.toml](./pyproject.toml).
