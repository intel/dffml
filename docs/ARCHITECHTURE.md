# Architecture

When applying Machine Learning to a new problem developers must first collect
data for models to train on. DFFML facilitates the collection of feature data
to create datasets for models to learn on.

![arch](https://github.com/intel/dffml/raw/master/docs/images/arch.png)

DFFML's architecture can be thought of similarly to a search engine. Each
**Feature** a developer defines searches for data associated with the unique key
its provided with. Once the data is found it is added to a **Repo** (repository)
associated with that unique key. A **Feature**'s search for data is dubbed
*evaluation*. A **Repo** holds the results of each **Feature**'s evaluation.
Results are stored under their respective **Feature** names.

To define machine learning a model within DFFML, users create a **Model**.
Models are responsible for training, assessing accuracy, and making
predictions. After evaluation a **Repo** can be used by a **Model** for any of
those tasks. Defining a machine learning model as a **Model** allows users to
quickly compare accuracy of various models on their gathered dataset.

Once the best most accurate model is known, users can easily integrate use of
the model into existing applications via the Python API, or a **Service**.
Services provide applications with ways to access the DFFML API over various
protocols and deployment scenarios.

## Classes

- [Feature](FEATURE.md)
- [Source](SOURCE.md)
- [Model](MODEL.md)
- [Repo](REPO.md)

## Original Architecture Drawing

![oarch](https://github.com/intel/dffml/raw/master/docs/images/oarch.jpg)

> December 26th 2017
