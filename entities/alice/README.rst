Alice
#####

See https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/
for more information on Alice. She is our developer helper.

Install
*******

DFFML currently **supports Python 3.7 to 3.9 on Linux**. If your distribution's
package manager doesn't provide Python 3.7 through 3.9,
`pyenv <https://github.com/pyenv/pyenv#simple-python-version-management-pyenv>`_
is another good way to install it. You could also use the docker container.

**Windows and MacOS are not officially supported yet**. Support varies by which
plugins you install. We do not currently have a list of what is supported and
what is not supported on those OSs. Most things should work. However, until we
are testing for everything we won't declare them to be officially supported.
Please create issues for any problems you encounter.

First make sure you have the latest versions of ``pip``, ``setuptools``, and
``wheel``. Some ML libraries require them to be up-to-date.

You may want to first create a virtual environment to avoid any permissions
issues when running ``pip install``.

.. tabs::

    .. group-tab:: Linux and MacOS

        .. code-block:: console

            $ python -m venv .venv
            $ . .venv/bin/activate
            $ python -m pip install -U pip setuptools wheel

    .. group-tab:: Windows

        .. code-block:: console

            C:\Users\username> python -m venv .venv
            C:\Users\username> .venv\Scripts\activate
            (.venv) C:\Users\username> python -m pip install -U pip setuptools wheel

.. warning::

    Make sure that if pip is complaining that directories are not in your
    ``PATH``, that you add those directories to your ``PATH`` environment
    variable!.

Install latest known working version

.. code-block:: console

    $ python -m pip install \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=dffml" \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=dffml-feature-git&subdirectory=feature/git" \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=shouldi&subdirectory=examples/shouldi" \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=dffml-config-yaml&subdirectory=configloader/yaml" \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=dffml-operations-innersource&subdirectory=operations/innersource" \
        "https://github.com/intel/dffml/archive/a2f2a1422e9f5792d306b3c43c79d0921bf85c21.zip#egg=alice&subdirectory=entities/alice"

.. note::

    Add ``-log debug`` to any ``alice`` CLI command to get verbose log output.

please contribute
*****************

Alice will be working on our repos with us, we are going to use the ``please
contribute`` set of commands (we'll overlay to ``alice.please.contribute``).

recommend community standards
-----------------------------

.. note::

    Tutorial on how we made this: https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md

Create a new git repo and add some contents

.. code-block:: console

    $ gh repo create -y --internal https://github.com/$USER/my-new-python-project
    $ my-new-python-project
    $ echo 'print("Hello World")' > test.py
    $ git add test.py
    $ git commit -sam 'Initial Commit'
    $ git push --set-upstream origin master

Ask Alice: please contribute recommended community standards to the repo

.. code-block:: console

    $ alice please contribute -repos https://github.com/$USER/my-new-python-project -log debug -- recommended community standards

Visit
https://github.com/$USER/my-new-python-project/issues

Merge pull request with README. Now the new project has a README!

**TODO** Link to docs on how to extend for org specific custom README templates.

shouldi
*******

.. note::

    Tutorial on how we made this: https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md

Alice's initial functionality is based around
https://intel.github.io/dffml/shouldi.html

We provide Alice specific overlays
(covered in https://intel.github.io/dffml/examples/dataflows.html) which enable
Alice to provide us with additional information on top of what shouldi already
gives us.

We can also apply organizational policies to our Alice via the overlay
infrastructure.

use
---

Check if a Python package is something you should install and use from security
perspective (aka does it have any CVEs).

.. code-block:: console

    $ alice shouldi use httptest
    httptest is okay to install

reuse
-----

Example CLI invocation asking Alice if we should reuse a git repo as a
dependency.

.. code-block:: console

    $ alice shouldi reuse https://github.com/trekhleb/javascript-algorithms

The response should be similar to the following

.. code-block:: json

    {
        "https://github.com/trekhleb/javascript-algorithms": {
            "static_analysis": [
                {
                    "critical": 1,
                    "high": 1,
                    "low": 0,
                    "medium": 0,
                    "report": {
                        "npm_audit_output": {
                            "critical": 1,
                            "high": 1,
                            "info": 0,
                            "low": 0,
                            "moderate": 0,
                            "total": 2
                        }
                    }
                }
            ]
        }
    }

contribute
----------

Let's ask Alice about a repo to see what she knows about the health of it and
it's community. This will help us make an informed decision as to if we should
contribute.

With overlays, Alice will be able to tell us if our experience / skill set seems
helpful to contribute to open issues.

Her analysis of the project will also let us know they are ready for us to
contribute (are they too backlogged, to they not have governance or contributing
docs).

.. code-block:: console

    $ alice shouldi contribute -keys https://github.com/trekhleb/javascript-algorithms

The response should be similar to the following

.. code-block:: json

    [
        {
            "extra": {},
            "features": {
                "author_line_count": [
                    {
                        "Oleksii Trekhleb": 7
                    },
                    {
                        "0xFF": 1,
                        "Aldo Salas": 17,
                        "Anton Kazarinov": 1,
                        "Antonio Gonzalez Capel": 4,
                        "Bravo Yeung": 1,
                        "DS Park": 75,
                        "Dar\u00edo Here\u00f1\u00fa": 2,
                        "Elif": 20,
                        "Felipe Veronezi Peters": 71,
                        "G\u00e9rley Adriano": 3,
                        "H2rmone": 1,
                        "Halil CAKAR": 1,
                        "Hyewon Kwak": 1,
                        "Israel Teneda": 5,
                        "Kim Chan": 1,
                        "Kirill Skvortsov": 49,
                        "Kush Gabani": 2,
                        "Lucas De Angelis": 24,
                        "Marcio Flavio": 1,
                        "Matheus Machado": 54,
                        "MrBrain295": 1,
                        "Muhammad Affandes": 2,
                        "Muhammed Erdin\u00e7": 199,
                        "Oleksii Trekhleb": 1591,
                        "OscarRG": 11,
                        "Perry": 3,
                        "Piotr \u0141ysik": 1,
                        "Rafael Ara\u00fajo": 36,
                        "Samay Sagar": 2,
                        "Sewook Han": 40,
                        "Seymur": 2,
                        "Suman kumar": 0,
                        "TheJang": 1,
                        "Trang Nguyen": 343,
                        "William Joao Cubillos Quintero": 1,
                        "edegil": 26,
                        "ilkererkek": 21,
                        "jackbyebye1024": 4,
                        "joaojgabriel": 4,
                        "kimzerovirus": 25,
                        "kyong4": 2,
                        "liamlylehr": 57,
                        "m11o": 1,
                        "observer.js": 36,
                        "qiugu": 49,
                        "rmagillxyz": 9,
                        "szhou": 1,
                        "tusba": 7,
                        "\u513f\u65f6": 73,
                        "\uc11c\ub2e4\uc194": 37
                    },
                    {
                        "Oleksii Trekhleb": 2861
                    },
                    {
                        "Oleksii Trekhleb": 457
                    },
                    {
                        "Coco Guerra": 20,
                        "CodingInvoker": 1,
                        "Deniz Binay": 363,
                        "Freivin Campbell": 102,
                        "Oleksii Trekhleb": 2945,
                        "justforever": 1
                    },
                    {
                        "Abdessamad Bensaad": 326,
                        "Adjie Djaka Permana": 303,
                        "Alexander Belov": 0,
                        "Andy Chen": 0,
                        "Anmol Gomra": 119,
                        "Askhat Arslanov": 23,
                        "Austin Theriot": 37,
                        "Avi Agrawal": 299,
                        "Brandon Villa": 1,
                        "Brian Tomlin": 1,
                        "Donghoon Song": 149,
                        "Eugene Sinitsyn": 1,
                        "Go": 1,
                        "Hanseung Yoo": 108,
                        "JD Medina": 22,
                        "Javier Savi\u00f1on": 164,
                        "Jos\u00e9 Vin\u00edcius Lacerda de Arruda": 16,
                        "Jo\u00e3o Pedro Raskopf": 262,
                        "Kirill Kazakov": 303,
                        "Luan Caldas": 6,
                        "Matheus Bonavite dos Reis Cardoso": 52,
                        "Oleg Maslov": 23,
                        "Oleksii Trekhleb": 6202,
                        "Riccardo Amadio": 294,
                        "Rodrigo Stuani": 1,
                        "Sagid M": 1,
                        "Sherlyn": 120,
                        "Xiaoming Fu": 1,
                        "Yanina Trekhleb": 328,
                        "Yura Sherman": 1,
                        "bhaltair": 1,
                        "deepthan": 1,
                        "dependabot[bot]": 6,
                        "lvzhenbang": 1,
                        "vladimirschneider": 1,
                        "\u8463\u51ef": 302
                    },
                    {
                        "Alexey Onikov": 5,
                        "Aykut": 317,
                        "Louis Aeilot": 4,
                        "Lo\u00efc TRUCHOT": 1201,
                        "Ly": 3,
                        "Oleg Khobotov": 1,
                        "Oleksii Trekhleb": 27
                    },
                    {
                        "Boardens": 135,
                        "Chao Zhang": 2,
                        "Ly": 1,
                        "Marcelo-Rodrigues": 10,
                        "Oleksii Trekhleb": 8542,
                        "Suraj Jadhav": 3,
                        "Thiago Alberto da Silva": 1,
                        "Yong Yang": 1,
                        "gifted-s": 72,
                        "solomon-han": 1,
                        "vladimirschneider": 1
                    },
                    {},
                    {
                        "Oleksii Trekhleb": 2
                    }
                ],
                "authors": [
                    1,
                    50,
                    1,
                    1,
                    6,
                    36,
                    7,
                    11,
                    0,
                    1
                ],
                "commit_count": [
                    4,
                    66,
                    6,
                    7,
                    16,
                    106,
                    9,
                    28,
                    0,
                    1
                ],
                "commit_shas": [
                    "cb7afe18ef003995d8e23cc0b179ee7e37e8a19e",
                    "7a37a6b86e76ee22bf93ffd9d01d7acfd79d0714",
                    "9bb60fa72f9d146e931b4634764dff7aebc7c1a2",
                    "4548296affb227c29ead868309e48667f8280c55",
                    "6d2d8c9379873d0da2b1262a14dd26d0f9779522",
                    "83357075c4698f487af733e6e0bf9567ba94c266",
                    "ed52a8079e1ad3569782aa9a7cd1fa829d041022",
                    "929b210b8e02cd77bdc3575a4e897ad24ad64ad3",
                    "ba2d8dc4a8e27659c1420fe52390cb7981df4a94",
                    "ba2d8dc4a8e27659c1420fe52390cb7981df4a94"
                ],
                "dffml_operations_innersource.operations:github_workflow_present.outputs.result": [
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true,
                    true
                ],
                "language_to_comment_ratio": [
                    9,
                    9,
                    9,
                    9,
                    9,
                    9,
                    9,
                    9,
                    9,
                    9
                ],
                "lines_by_language_count": [
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    },
                    {
                        "javascript": {
                            "blanks": 3476,
                            "code": 14025,
                            "comment": 4140,
                            "files": 330,
                            "lines": 21641
                        },
                        "json": {
                            "blanks": 0,
                            "code": 9607,
                            "comment": 0,
                            "files": 2,
                            "lines": 9607
                        },
                        "markdown": {
                            "blanks": 0,
                            "code": 15813,
                            "comment": 0,
                            "files": 191,
                            "lines": 15813
                        },
                        "sum": {
                            "blanks": 3476,
                            "code": 39445,
                            "comment": 4140,
                            "files": 523,
                            "lines": 47061
                        }
                    }
                ],
                "release_within_period": [
                    false,
                    false,
                    false,
                    false,
                    false,
                    false,
                    false,
                    false,
                    false,
                    false
                ],
                "work": [
                    0,
                    68,
                    0,
                    0,
                    25,
                    56,
                    36,
                    5,
                    0,
                    0
                ]
            },
            "key": "https://github.com/trekhleb/javascript-algorithms",
            "last_updated": "2022-05-20T08:41:16Z"
        }
    ]
