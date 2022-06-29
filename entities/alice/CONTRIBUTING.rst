CONTRIBUTING
############

**TODO** Test this with the modified consoletest which doesn't
just take blocks with ``:test:`` on them (so that they render
on GitHub).

This document describes how to write Open Architecture overlays,
overlays for Alice, how to work within the codebase, and the
contribution process.

Debugging
*********

Add ``-log debug`` to any ``alice`` CLI command to get verbose log output.

Run within the builtin Python debugger to be presented with a
Python interpreter breakpointed at the raised exception.

.. code-block:: console

    $ python -m pdb -m alice

Cloning the Repo
****************

We are currently on the ``alice`` feature branch of DFFML. See
https://github.com/intel/dffml/pull/1401 for more details.

.. code-block:: console

    $ git clone -b alice https://github.com/intel/dffml

Now open or change directory to the directory containing Alice's
source code within the DFFML project: ``entities/alice``.
``dffml.git/entities/alice`` therefore means, the path
to ``entities/alice``, where the parent directory is wherever
you cloned the ``dffml`` git repo to above. If you were in a shell
at the root of the source tree this would be your current working
directory, the same as the output of ``pwd``. The directory itself
in the following example is just named ``dffml``, which is the default
for git to name based off the repo name on clone.

.. code-block:: console

    $ cd dffml/entities/alice

Installing in Development Mode
******************************

.. note::

    If you installed the package not in development mode
    off the README's instructions you'll need to uninstall
    all the packages you installed **by name**.

    .. code-block:: console

        $ python -m pip uninstall -y \
            alice \
            dffml \
            shouldi \
            dffml-feature-git \
            dffml-operations-innersource

Run ``pip`` with the ``-e`` flag to specify an editable install,
this must be done for each package.

We select the ``dev`` extra from ``extra_requires`` group to install.
This group is given in the ``setup.cfg`` file. It contains dependencies
which are referenced in the documentation and must be installed when
working on Alice.

We do not select the ``dev`` extra on the other packages unless we
intended to do development work on the as well.

.. code-block:: console

    $ python -m pip install \
        -e .[dev] \
        -e ../../ \
        -e ../../examples/shouldi/ \
        -e ../../feature/git/ \
        -e ../../operations/innersource/

Data Flow Programming
*********************

Data Flow programming focueses on data types and data transformations.
Data Orented Design is also helpful in understanding Data Flow programming,
altough a distinct concept itself.

- https://en.wikipedia.org/wiki/Dataflow_programming
- https://www.gamedeveloper.com/programming/tips-on-writing-code-for-data-oriented-design
- https://www.youtube.com/watch?v=aPh4Z3SioB8
- https://github.com/intel/dffml/blob/alice/docs/concepts/dataflow.rst

Finding Data Types to Work With
*******************************

You can leverage
https://mermaid-js.github.io/mermaid-live-editor/
to visualize dataflows. Copy paste the output of the diagram code into
the webpage to edit and visualze the flow.

You can also install ``dffml-config-yaml`` via ``python -m pip install -e
configloader/yaml`` which gives you the ability to dump to YAML via addition of
the ``-configloader yaml`` option.

The JSON or YAML document's ``definitions`` field can be useful for finding new
data types available within the flow.

.. code-block:: console

    $ dffml service dev export alice.cli:AlicePleaseContributeCLIDataFlow | tee alice.please.contribute.recommended_community_standards.json
    $ dffml dataflow diagram alice.please.contribute.recommended_community_standards.json

.. image:: https://mermaid.ink/svg/pako:eNrFXP1vozdy_lcW219sILfg98eiOKBN-hHgrglyKfrDbiGQw-GuGlt2JTmpEeR_70O9sqS1c5q3PXv3ctl1ZHLI4Qxnnocc6tfXdNP49dvXH9bl9uOrH795v9rc1ek_SvS5qKhMVjFyI082di7KmtCLSfrd9-sb4s1mufrw6i_b8oH_E52391cs9nzVl1dXb_-u9GZTqv6rzXZ98xPjA0cllpMpcC9ec6iWOPdqSguemFxmCsFzVe_K1ZL4DV0t3_zD-On7Ky4b_vpmtV0v692Wf2C6ub7mVeP2NX64Wy2395jqqpV127ylNZctL_Bnu-YF5sSLZV-sbrYL_p_lZrs56CNNY69P7901PmiDJhz1-1WOQVkbuHL22jeluvaZvIcclYrnF1cilxxC5GqdsUklSs4wNd16xJSY_cW-M2FIXm03l3KXV3_4wx9fSYq9XyVjerYcqfoedLStpEbVOFVKs6QNRr69uZTbzRyOWjLFxG6DUdXq1qoxGb9x3bjiasJwm7ur7aVsk92Akrj3KxjlxFuDoxTZ6aC8dXY4OsWYILF5pXP_G731wx322mIs2AIehk23WG4Wbblm2t6s7w--Kk3ivK_amlvU5GxvqrYWggqqhw7PN7CR6y-sgiey2GBY7FpdtJptKvi3FViGdLUXJ30v5eY7K0oqwRngb1mTdrYZxjJko2JtKQyfD7HXo9tIsiY_FcQ9dRtjXYwx9BwU3M-HHnxuHAu3XnT4m9b8u595fVXudx2_u-V12S5vVpt_WW7fflhuJ1Nsbxa7ERYPn5z40vmZnfelElh5uCH8zlUDISGW0lMomVwtsX4JvWAb5SJpG2qxVJXjUnxRhrr3NZb2EJCkdjtDSwpiCWJADGmGyCekigqHINtciTlkBaFHz5JkTQMK4p54Vg0-ImYbUiZkTtYzgiz-JHLeaH4OC3z9p2_fQsDiY5l29jFrSqOf956K3exjyMF1rTv2Nv7oWYfW2OTO7qXmrnLQ3JVG9huLnxXVhA2uAGmUqaQv6Lpdys129pJ0QOKzqsVQulY5cna1N_hbUib5rhq7ePFLQU4eA0otZw5ousaCp0gWGIZ6ynDm3EuuXgevuz96pCRrN6Ak7rFHYgelQiHHDjzVe4Nz6BAaJeVs7s_rkcgtZfPTyDL9Zg37Hnou6KErUsm-78FrpRkK-ZMVAxsoskr7YruuRiNsAGxU40suX1K_FgtyF5Bc11RSdEVp4IMQTYHBkrZ7z5aaTUlV0BMbBD9Ytr04bXqoCjGsqUClqtQp6RMsJsnaDSiJe-xoZJRSPnlbe9UhN4SdEFXkboD5VKrPbIhrxj5d3KwW24_LzadJVJrJeYdKADjZeYWlcak17ZruzkeFvOwaPW8Y_Gt61GSyrSpXm32rFj6RXa6hUrZedSTNyXGkZjs7SvqMuJNDgQjuOjdHmrwKEYYPHJyuMRxDotRy5oApsDY5xuw7K6fZecwbSD-pYLXNJ_BPkjUNKIh77KnFavizLwWSso5Ga92qd2AcnSjY9JwWXt-thnE_8U9pfAHkWYIvax2QhxKyRFAZm7IiS1BIsfaXm31ntqoo2CGDlNXQFVF1BVuqdOtafoByUrsJWQlqPDaaAeXoDd6tOCQGa2w6wxcq2QyYnJ4Fsw8wS4ceDwz_uh0sJ01CAFhooZoBPvO-GR882AyyXgihRF8cvbAKtlVyKSbyXAnGAcWGKqwyAj-CRbqoGO1SbjfhHkGX9yvkCHyunA8O8QKQHsCtqQj2ht3bar4YyoAnXIOhlg9jYKnHzIGbKgVUPNaYK_C8UmQYEcGUEoGGfXlwU6ndzOHg6gO_ZI4m-zgSqYf_Iq_mRK63foLvBFlTnhfEPd4XOescNZzS-O5SqcllG8iDH3OkUPVzOVXjLa-vl6vF8JJFXZcVfTzsC2kSAoQD13XdFJVzdTB30Y4B69vAvEnV-sIqWF9daN04gAUFWORDbfB_ctob70y4aNwLLLjvcSn3mAwpaAVm4IoG34WLBzID6nrdiumOEBtjMifMQJI1MQNB3GPP6ejIPtnqQGmMQaZNY3tjpFhC6PmZlv1f7-q3m80dP5ybXvO2APjgk4P7SDMRTnvRg2rBbiZfa0I8tlgpW0IDHqjms-gxaGKMHY4QdLUWpMwrS5a94-RaKhf1pt1fyu2m4yxBIXiOQoCMGYtjM4UWI9C5VsBiwBGR6HDKK7WbOVwEAPPKMOkCykCquwwXq4AvNraS1cV2ub0aEVxqOHM83UNBBLaZU1W9xnH6wj2PqVd2IZ6cKguydgNK4p4c4iD2sokNMy5oqzobH6MnNCYddXtuhzp60mK4yfE4R5jH-W0RwQGc7thXySHNKYb-jTVHJvA4Vi-vRaoZabxh_k4nE9k6jRmVlrmUkkg9AA6p3c6IkjojvZLtyETOg0oDV7feK4gDp6K6R0Z9uHTZzfFSbj9z2JZSj0q17rPtHBDIkBDGZZxJOXHQD8Pelu3IHVLzmaOa3Ylwqn54sDbK1EDaVasN6Z6MO0QAod3c4XLwKjuQMaOaxm9grmAMpaTZNJWPO1KSNaUqQdyTQyxQOVDAwI4zpRoRXtiAjEI-FSjy3L58uJ47RajHAythNuf3pevBYTFCyWbobJxlOJvpBIfX2NefS5fIpWatItVqTDNoRT4HUxNTjY7ixbSX79ZXl3LjnVUlzcBdgWGLSYCI-J8fRD3E4MehbivWNnV0I0nWxCEFcU-wMja384ikjlrKBWDVjkNHrnl3c5dfaOk_BTvSJASsHJDTjQEANMHC-bTVBXu6gTTUWnN9YRVsgcEthvZVuxaYHMiMAp2xmBZ4-wPOkdpNCFnQBUCgxgT-qcb9Rc0uxwbAZAEObco2lf4Q5aR2M4dT1FUG-1UIl80xISzZ3prF770DSjvgHKnhzPGs96bX4jIiNHiDcgkfjHO10sZNlDkhAIKsaUBB3BMC4DJ1x9GNE3cHZFE5Ij25VJMCPHTP50vf311d_cD_fceb7YNH3a6P8F-Yh3AexsUlZDTuI5lWyNJg2GagpabD59BCxaxqp540AlHOPpWYjTPjGo6LVu0B50jtppgmqAMjupB88yoYXXO3utnIClFQa9UbxD_sQandzOFCV4kRfH2j7KzrSSWTm3f4ED6Y68VHLMWl3G7mcBYMCfQveAOczr63omPVpUekoA78e3GzXn5Yri7lljMHrIMiKUTjqg3XZh0lZDqvwBO8ZaMeYozUbuZwqttaQ09A9FW1XGIHWsrjkBTMBZ8cY4zQcOZ4sXLoQWU1LtQAyox3vYdkg9VeI_-cXIgLsiaoKIh7HGOisZGgSLXJGnQsvY0L9Jw0RmBdX2R3_sCd17wi_iSH3a4_pVfS1AR6Ra5mimmU-oSsbcy2llBcsGog2_5FFAORUs56HRSmVLtWjOQAp_HjOqwp84QCCe0nkwuawnM8AxN3k1RNFLxukFdtrDmqUb9zUnQhyZqcWhD32MdS5KoreITnppB_RymdGzw_jtoOZT-vKXb79-Bk0twEJ2umwUMbxVHbVMkXj7VwumpsOZ_9l9HM6wzSA8ZGyCXjUtXEgFSmALmCg3qPvUxqP3mZoCpAXgqAVzlbLFum6iKIexiH4-Sj61GfeJkgazoVEsQ99jIfmy2egKeSUcAo2WcEPhV7TS04q5_PFv-xXm5LvUKP65stb_55fXP9_Ti43mxGxdXbcjXW935x88vq0cW3NEXhHBX0gzNXb8C6FIeWB7RtvbSGVNS_rII1hqiBtg1CB5JNc8g72XedyNpQajhkaaHdvl7wvKajaKdXhTRrMtIa3KdwbiYiH-toVN25-MMJpCBrX7RzXtyTy86QQJ0ayCFasFLWVT9OA7urxrF9ljOCT2v49ofa0xXHVM-84sdV2dK0zvuXdpo1AI0Hss-GKHFwLndHjkYVcv7sShH41Lic9sEaJlW0CSbQqLjs40LHXqzK9e5eUmg3hRNBO4ixHqGPqmlsuzGxG9B9CwSlEHpCOtxLSu1mDgcHs-CDpWCScPyGXyIw9Mo2aaJIRxeWZO0GlMQ9OWsh06MfRRgAxx6EzmhPOQTVeog-mue39u_WOt-tr44nL8KUBPdl0AykK8DiosHDuyupIJ0Zw5wg5bMqlC2m1WNC8sq1UgayQNDxlogMcJR5VLYtNZ9cSlBwHCaDyblWrfUe9MCWaFMHuEnj7A3c6MSlBFlTVBTEPTmvqDkXKinVWEwb5WkQCretI7M3317IAtwe2-Dm0GhX6XzqY9Icz_tYC6GM-ucGFousVUmr0Aa7SuMEJ5kvq6En3YDMQwzgiXY8VYGSZPt4v1Gjn-4c9gfGUtsppgjqjoIzlz2wv0lgm4ZzVuTsuEEpJvkcw9HjJFn7at3z4p6yVxWD0Sla5PddxVkNNMgx8BXc238ee4wSwQ1y184U-2T2Yfkzr06o7Pl5nvc6ZXVHYglkFUgWY_FGuYli7wIWrLgvr6Wy4EsEpNVgY1IhBJNKiZ0KuWiNPfU8qe1U3CqojJBJuqtxfNUSUmNtkFYqHAXe4m1rJ8UZkqwJcgriniDA2C27qoutyLKj0qxk9GUVdYaQfVnz4nZnisUnFV9nq5IXN5M9dqt8fY-Offnh7W75nr5skiYhlLulbhPlBlw8TgItIwU5T8gBMSRtX1oFaxpwm8Vi26yU7trV4E1NNofugj7cHUjtpsAh6PJ-VSiUXUFgsgxi79EBBoc4Rq518aT6WpI1nYEI4h77C8TQqBzzRuUSAdApgWIo4J3UFbDaO_rI9NPAwD9j2dvhhc5mOZZr8e8__OlgdUnUeat3H-Pg3c6OovFxJVdtZ-W1tgDNTs2aSHROcUTq5NRTcKNKzhkdTAUzxyqZCzS7lJvtVlKa0PtVYjuOvDRyNPmmdveIVkOkGg9otbrYzfRS1m2qRhakPalG7thJxjSNRi2PA5IM4s4hxfHKA6iGrgZrefJUTOonoFmP5NBb9d44KNObL60Wdtmp0lLzT0dlbnHENy4efEGRjYlCtNlbr1XOtLeJ1GyCmsLooybEZ5OomeBbM-RcC3FUtvWgKFXlLzabj4uf-P5SbjpzRMfAZ1zyeBYGqwWuPY8KWAQ7i8BNh7tGQdJ0FS4IG5VgmCgr_FWwMqlmeI2Bd2XVAyGB__rXtsdvct-ZGj-OIPAiD2uNIm0EAM4OoT8mb3e8Ibw7PPP7tB7yJG6cF3DeIZEtVTBYMQ2fRuD1sKcdr6DwH5zZnhleJ8RFsAi0bDvsV5rBhmCKKkVOh7Mhqd1u2aR5YKYxeE26wuMAarNrnVLT-KFgrQOQwaFOVJI1DSiIg2eSJUCErsdDyOTCmHUppFLmVIIxv_4OaPpN7jZT3U-9xGpvkRSVbQQQDc42YGbSSmeAaeS0d4eE_G_8y4_3t8eTcKmn4B6lcgFXHI9jB2rXCul6nLrBptSs_71xi2Pwy2xa8s1Wlayqo8wKYMZGi5T7cL4jtZsWSpgAEGNw47nxuNEwbHzDtozcSrX4ASiPLra3l3KrmYN9ahUYuGDy3AxDbimqJx17AP9uVKsyx9W5vl9MPy1u1zf_BbC0GItwMJIk6LyRGBE3sPag_i1h5WroeXhcAdOHO9GMaSBYmgbOqIcnJrDpqrA3AkBaBBhJ7WLqdim33C2kNKPxrDQG7iNWma6KTxn_JuRw7BsDTHHyFkmSNRELQdwThhmUBnZIAC8WidurbovfbUZ8Albx7gTglrY4rltf31wf8e7AU48OayXJ0mlXCnCFUCgnbSrgsG4mqqDcQDMl_3_mVXMHakIyQB4qIQIfwMdijshTWqXSLg7dLuXG-yOr87Mc5tXRjC-6GPdurprcjXKlFQ4ZMCny6ZHVeVl7854X96RwMQMADM5Hsasw4HNm_MTBAvurerIxd-l-V1f-sJTHekNBiHCt4wOgYeJYXTOm-BL1KNrrBiCtMPDl-SnYUXQELktGRUWmdyyTJluRPvFBq8cNKbWceLAwm0G8UwqgnbA9zG7BoVOm4irgi09Onxz5SLL2xPu8uL3FHmFyl0wE-zIeETmiYfbkkRJALNhUru--Bmld3d0-_hYeoZv0LTyPLhyBpKAY_j_utIBnNXzOBmTPrGo24d13d9vbu-2jOUi9_m9zWK4wwubdt7u_DmNMnz64XWgAt0c5eiDA3fWDSsZ4Qmyk7FvYvWl2Hr8vHkD4YgOm8Pd1_ccBzt4cdv6b6e74zck340iSJjMLX58jf-fIRN6Er8WRv2BippjQuTc09-OsLtbgkTPAGaID6NDdu0-X53CQL3Wb0IPwJS0y13n4VpWz38iBkGmS14F6UUi-FrjJWAZqxfKa8YCwHJRovV9fvbnbLq92p4hf__mbS7n3PuCe_9YH-dn7_k3y-e9y-Cy6SO_8P8skpDfjMxdUegkuf-_FdDgjPBWW34rPFCM9jpsKaIWXr3IB-_QtVsI71pmxSHqfOjMWyWKkq919cfH5N48yL54pRnobshMjvaObucTS-7iZSyyLAWBs1oFFZTDf2qD7KE6Bt0XoFJ0-bOw_87bs6q5-3JeBSj2n4inh3d1M_5ceYskV6_s30-cfVslfGzc5rvBSaq6NhRdQc20sipm1NtJDGkTxBlJJ1JQB99ZIe8MBkPUCqEm0hg6u8sMOKe2c5R-nim-p67QDhacZM5dVenIxc1llMWD1pWIdaytaMbgf1hm0EGoAXMNTf289fjy80zjfd4IYwmOOmZtHqu6Xy2SnEwuhal_-woEpQArV-HKJ295ZztfYz3QWqXZ-prPIYqSizslSQmX93DAnFE_PFCNVx85dYqHwce4Si2IMMEGHFI91b8ljTskn3VVVBO07HzHqdE7_ZjqWfrM_bJW6TwhKqLibuSZSJd3MNZHFvCSbk2q35LKsPSk8X5AzU4xUXTHTMtKl-0zLyGKkip8pKQv3yDPFSFefu--cHF8Ky60CumpEUwc8g38sMgni-_FQ5HDZdbzmlPruEdz5u1D5snsPr89fMM48QZAu3OAs8Ggs6ijLL7UjvTWQpb578kvjgOewIMvV5pZp-2bB17fb-_1fl7KAqZhCuOD5XPOQ7n7kw89pDwo3H3Ixyj5_nT9hlw_P93vw_LHv7kjx9Vevr3l9XZbt9dvXv75fvXr1_vX2I1_z-9dv8eM-Vbx__X71G5re3Y5j6H9q48779dterjb81etyt735y_2KDh9Mrb5Zlg_rcr3_9Lf_BQXd4ms

Making a Game Plan
******************

Since we're thinking about data, we need to make a game plan, we don't
want to get caught up writing unnessicary code. We don't want to deal with
production or development database configuration, we just want to figure
out how to get the data we need, then figure out where / how we can plug
that data extraction, that feature extraction, into the any applicable
collector flows (https://github.com/johnlwhiteman/living-threat-models).

We want to enable collection of the ``name`` field within the JSON file
``.myconfig.json``. Here's our game plan

- Check if the ``.myconfig.json`` file exists within a directory.

  - If it doesn't exist, bail out, go no further
  - Read in the contexts
  - Parse the contents as JSON
  - Return the parsed contents

- Validate the contents conform to the expected format

  - Input validation using JSON schema
  - If schema validation fails, bail out, go no further

- Return the ``name`` property of the parsed contents

.. warning::

    **SECURITY** The if statements in the first list item where we check for
    file existance within this operation happens within and not as a
    distinct operation on purpose to avoid a TOCTOU issue if the lock on the
    directory were to be released between time of this operation and
    time of the next, so we contain dealing with the resource to this
    operation.

    References:

    - https://github.com/intel/dffml/blob/alice/docs/concepts/dataflow.rst
    - https://github.com/intel/dffml/issues/51

Writing Operations
******************

Your base flow is your core functionality, it should be modular enough run
an on it's own with mock data. Think of it as the library behind your
functionality.

We implement off of our game plan, focusing on the functionality of bite sized
chunks. Leveraging doctests as our unittests.

References for writing operations, including examples with networking:

- https://intel.github.io/dffml/alice/examples/shouldi.html

**myconfig.py**

.. code-block:: python

    import json
    import pathlib
    from typing import NewType

    MyConfig = NewType("MyConfig", object)
    MyConfigUnvalidated = NewType("MyConfigUnvalidated", object)
    MyConfigProjectName = NewType("MyConfigProjectName", str)
    MyConfigDirectory = NewType("MyConfigDirectory", str)

    def read_my_config_from_directory_if_exists(
        directory: MyConfigDirectory,
    ) -> MyConfigUnvalidated:
        """
        >>> import json
        >>> import pathlib
        >>> import tempfile
        >>>
        >>> with tempfile.TemporaryDirectory() as tempdir:
        ...     _ = pathlib.Path(tempdir, ".myconfig.json").write_text(json.dumps({"name": "Hello World"}))
        ...     print(read_my_config_from_directory_if_exists(tempdir))
        {'name': 'Hello World'}
        """
        path = patlib.Path(directory, ".myconfig.json")
        if not path.exists():
            return
        return json.loads(path.read_text())

    def validate_my_config(
        config: MyConfigUnvalidated,
    ) -> MyConfig:
        # TODO(security) json schema valiation of myconfig (or
        # make done automatically by operation manifest schema
        # validation on InputNetwork, maybe, just one option,
        # or maybe similar to how prioritizer gets applied,
        # or maybe this is an issue we already track: #1400)
        return config

    def my_config_project_name(
        config: MyConfig,
    ) -> MyConfigProjectName:
        """
        >>> print(my_config_project_name({"name": "Hello World"}))
        Hello World
        """
        return config["name"]

Run Doctests
************

We can run our doctests using Python's builtin helper.

.. code-block:: console

    $ python -m doctest myconfig.py

Writing an Overlay
******************

Overlays can be as simple as a single function, or they can
be classes, files, dataflows, anything which you can generate
and Open Architecture description of (which should be everything
provided an ``OperationImplementationNetwork`` is/can be implemented)

**alice_please_contribute_recommended_community_standards_overlay_git_myconfig.py**

.. code-block:: python

    from alice.cli import AliceGitRepo

    from myconfig import MyConfigDirectory

    def repo_directory(
        repo: AliceGitRepo,
    ) -> MyConfigDirectory:
        """
        >>> from alice.cli import AliceGitRepo
        >>>
        >>> print(repo_directory(AliceGitRepo(directory="Wonderland", URL=None)))
        Wonderland
        """
        return repo.directory

Run our doctests for the new overlay.

.. code-block:: console

    $ python -m doctest alice_please_contribute_recommended_community_standards_overlay_git_myconfig.py

Registering an Overlay
**********************

The entry point system is an upstream Python option for plugin registration,
this is the method which we use to register overlays. The name is on the
left of the ``=``, the path to the overlay is on the right. The ``.ini``
section is the connonical form of the system context which our overlay
should be applied to.

.. note::

    If you are working within the exsiting alice codebase then the
    following ``entry_points.txt`` file and the
    rest of your files should be in the ``dffml.git/entities/alice``
    directory.

**entry_points.txt**

.. code-block::

    [dffml.overlays.alice.please.contribute.recommended_community_standards]
    MyConfigReader = myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig

Reinstall the package.

.. code-block:: console

    $ python -m pip install -e .

Contributing a Plugin to the 2nd or 3rd Party Ecosystem
*******************************************************

.. note::

    We recommened doing this after you have played around within the
    Alice codebase itself within ``dffml.git/entities/alice``, packaging
    can get tricky and get your environment stuck in weird states.
    You can add and modify the files you would within a plugin within
    the core Alice code directly. If you intend to submit your changes
    upstream into the ``alice`` branch as a pull request you should
    also skip this package creation step and work directly within
    this codebase.

If you want to make your operations, flows, overlays, and other work
available to others as a Python package, you can take the files you
created above and move them into your package.

Run the helper script provided by DFFML, or write the package files by hand.

References:

- https://github.com/intel/project-example-for-python

.. code-block:: console

    $ dffml service dev create blank alice-please-contribute-recommended_community_standards-overlay-git-myconfig

Move the old files into the new directory
``alice-please-contribute-recommended_community_standards-overlay-git-myconfig/alice_please_contribute_recommended_community_standards_overlay_git_myconfig``

.. code-block:: console

    $ mv *myconfig.py alice-please-contribute-recommended_community_standards-overlay-git-myconfig/alice_please_contribute_recommended_community_standards_overlay_git_myconfig/

Add a section to the ``entry_points.txt`` with the the new versions of the
Python ``import`` style paths.

**alice-please-contribute-recommended_community_standards-overlay-git-myconfig/entry_points.txt**

.. code-block::

    [dffml.overlays.alice.please.contribute.recommended_community_standards]
    MyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.myconfig
    AlicePleaseContributeRecommendedCommunityStandardsOverlayMyConfigReader = alice_please_contribute_recommended_community_standards_overlay_git_myconfig.overlay

Install the new package.

.. code-block:: console

    $ python -m pip install -e alice-please-contribute-recommended_community_standards-overlay-git-myconfig

.. note::

    If you originally edited the ``entry_points.txt`` file in
    ``dffml.git/entities/alice`` then you need to remove the
    lines you added and reinstall the ``alice`` package in
    development mode.

    .. code-block:: console

        $ python -m pip -y install -e dffml.git/entities/alice

Now re-run any commands which you might have run previously to validate you're
new overlays are being applied. The diagram or please contribute commands are
good targets.

Registering a Flow
******************

You can write a base flow as a class and then give the entrypoint
style path to the class or you can write a file with functions and
give the entrypoint style path as the entrypoint.

**TODO** modify **dffml.git/entities/alice/entry_points.txt**
add the following, rename files first. Use this as an example
here after it's moved.

.. code-block::

    [dffml.overlays.alice.please]
    contribute = alice.please.contribute.git:AlicePleaseContribute

    [dffml.overlays.alice.please.contribute]
    recommended_community_standards = alice.please.contribute:AlicePleaseContributeRecommendedCommunityStandards

    [dffml.overlays.alice.please.contribute.recommended_community_standards]
    git = alice.please.contribute.git:AlicePleaseContributeRecommendedCommunityStandardsOverlayGit

TODO/Misc.
**********

- Example of running static type checker (``mypy`` or something
  on ``myconfig.py``, ``dffml`` has incomplete type data, we
  have an open issue on this.

- Cover how overlay load infrastructure can be added too,
  beyond these default only merge on apply `@overlays.present` (of
  which `@overlay` is an alias).

- In "Contributing a Plugin to the 2nd or 3rd Party Ecosystem"
  link to 2nd Party ADR.

- CI job to export dataflow to schema to validate lists of
  values for correctness as different definitions.

- In "Installing in Development Mode" reference pip/setuptools
  docs on editable installs.

- Covered in DFFML maintainers docs that unit testing infrastructure is
  slightly different, we want to intergrate the output of
  https://github.com/intel/dffml/issues/619 once complete.

- In "Making a Game Plan" link to Living Threat Model terminology
  within some general LTM page which has links to all resources,
  probably Joh
