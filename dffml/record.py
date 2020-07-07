# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Information on the software to evaluate is stored in a Record instance.
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from .util.data import merge, export
from .util.display import create_row
from .log import LOGGER

LOGGER = LOGGER.getChild("record")


class NoSuchFeature(KeyError):
    pass  # pragma: no cov


class RecordPrediction(dict):

    EXPORTED = ["value", "confidence"]

    def __init__(self, *, confidence: float = 0.0, value: Any = None) -> None:
        self["confidence"] = confidence
        self["value"] = value

    @property
    def confidence(self):
        return self["confidence"]

    @property
    def value(self):
        return self["value"]

    def dict(self):
        if not self:
            return []
        return self

    def __len__(self):
        if self["confidence"] == 0.0 and self["value"] is None:
            return 0
        return 2

    def __bool__(self):
        return bool(len(self))

    __nonzero__ = __bool__


class RecordData(object):

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    EXPORTED = ["key", "features", "prediction"]

    def __init__(
        self,
        *,
        key: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        prediction: Optional[Dict[str, Any]] = None,
        last_updated: Optional[datetime] = None,
    ) -> None:
        # If the record is not evaluated or predicted then don't report out a new
        # value for last_updated
        self.last_updated_default = datetime.now()
        if key is None:
            key = ""
        if features is None:
            features = {}
        if prediction is None:
            prediction = {}
        if last_updated is None:
            last_updated = self.last_updated_default
        if isinstance(last_updated, str):
            last_updated = datetime.strptime(last_updated, self.DATE_FORMAT)
        for _key, _val in prediction.items():
            prediction[_key] = RecordPrediction(**_val)
        self.key = key
        self.features = features
        self.prediction = prediction
        self.last_updated = last_updated

    def dict(self):
        data = {
            key: getattr(self, key, [])
            for key in self.EXPORTED
            if not isinstance(getattr(self, key, {}), dict)
            or (
                isinstance(getattr(self, key, {}), dict)
                and getattr(self, key, {})
            )
        }
        # Do not report if there has been no change since instantiation to
        # a default time value
        if self.last_updated != self.last_updated_default:
            data["last_updated"] = self.last_updated.strftime(self.DATE_FORMAT)
        return data

    def __repr__(self):
        return str(self.dict())


class Record(object):
    """
    Manages feature independent information and actions for a record.
    """

    RECORD_DATA = RecordData

    def __init__(
        self,
        key: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if data is None:
            data = {}
        if extra is None:
            extra = {}
        data["key"] = key
        if "extra" in data:
            # Prefer extra from init arguments to extra stored in data
            data["extra"].update(extra)
            extra = data["extra"]
            del data["extra"]
        self.data = self.RECORD_DATA(**data)
        self.extra = extra

    def dict(self):
        # TODO(p2) Remove dict method in favor of export
        return self.export()

    def export(self):
        data = self.data.dict()
        data["extra"] = self.extra
        return export(data)

    def __repr__(self):
        return str(self.dict())

    def __str__(self):
        try:
            width = int(3 * os.get_terminal_size().columns / 4)
        except OSError:
            width = 70
        header = "\n\tKey:\t" + self.key
        divider = "+" + "-" * (width) + "+"

        if len(self.extra.keys()):
            header += "\n\t" + str(self.extra)

        return "\n".join(
            [header]
            + ["Record Features".center(width).rstrip()]
            + [divider]
            + [
                create_row(feature, results, width)
                for feature, results in map(
                    lambda k: (k[0], export(k[1])), self.features().items()
                )
            ]
            + (
                ["\n" + "Prediction".center(width).rstrip()]
                + [divider]
                + [
                    create_row(pred, conf_val, width)
                    for pred, conf_val in self.data.prediction.items()
                ]
                if self.data.prediction
                else ["Prediction:    Undetermined".rjust(width)]
            )
        ).rstrip()

    def merge(self, record: "Record"):
        data = self.data.dict()
        merge(data, record.data.dict())
        self.data = self.RECORD_DATA(**data)
        self.extra.update(record.extra)  # type: ignore

    @property
    def key(self) -> str:
        return self.data.key

    def evaluated(self, results: Dict[str, Any], overwrite=False):
        """
        Updates features with the result dict

        Parameters
        ----------
        results : dict
            The results that will be added to the features.
        overwrite : boolean
            If 'True', the function overwrites the current features with the results provided.
            If 'Fasle', the function updates the current features with the results provided.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>> print(example.features())
        {'dead': 'beef'}
        >>> results = {"new": "feature"}
        >>> example.evaluated({"feed": "face"})
        >>> print(example.features())
        {'dead': 'beef', 'feed': 'face'}
        >>> example.evaluated(results, overwrite=True)
        >>> print(example.features())
        {'new': 'feature'}
        """
        if overwrite:
            self.data.features = results
        else:
            self.data.features.update(results)
        self.data.last_updated = datetime.now()
        LOGGER.info("Evaluated %s %r", self.data.key, self.data.features)

    def features(self, subset: List[str] = []) -> Dict[str, Any]:
        """
        Returns all features for the record or the subset specified.

        Parameters
        ----------
        subset : list[str]
            The subset of features that will be returned.

        Returns
        -------
        dict
            features.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>>
        >>> print(example.features(["dead"]))
        {'dead': 'beef'}
        """
        if not subset:
            return self.data.features
        for name in subset:
            if (
                not name in self.data.features
                or self.data.features[name] is None
            ):
                return {}
        return {name: self.data.features[name] for name in subset}

    def feature(self, name: str) -> Any:
        """
        Returns a feature of the record.

        Parameters
        ----------
        name : str
            The name of the feature that will be returned.

        Returns
        -------
        any
            feature.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>> print(example.feature("dead"))
        beef
        """
        if name not in self.data.features:
            raise NoSuchFeature(name)
        return self.data.features[name]

    def predicted(self, target: str, value: Any, confidence: float):
        """
        Set the prediction for this record.

        Parameters
        ----------
        target : str
            The target you want to store the prediction at.
        value : Any
            The prediction.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>> example.predicted("target_name", "feed", 1.00)
        >>> print(example.prediction("target_name"))
        {'confidence': 1.0, 'value': 'feed'}
        """
        self.data.prediction[target] = RecordPrediction(
            value=value, confidence=float(confidence)
        )
        self.data.last_updated = datetime.now()

    def prediction(self, target: str) -> RecordPrediction:
        """
        Get the prediction for this record.

        Parameters
        ----------
        target : str
            The name of the feature that will be returned.

        Returns
        -------
        RecordPrediction
            The prediction of the target specified.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>> example.predicted("target_name", "feed", 1.00)
        >>> print(example.prediction("target_name"))
        {'confidence': 1.0, 'value': 'feed'}
        """
        return self.data.prediction[target]

    def predictions(self, subset: List[str] = []) -> Dict[str, Any]:
        """
        Get the predictions for the subset of record.

        Parameters
        ----------
        subset : list[str]
            The list of subset of the record that predictions are returned for.

        Returns
        -------
        dict
            The prediction of the specified subset.

        Examples
        --------

        >>> from dffml import *
        >>>
        >>> example = Record("example", data=dict(features=dict(dead="beef")))
        >>> example.predicted("target_name1", "feed", 1.00)
        >>> example.predicted("target_name2", "deed", 0.97)
        >>> print(example.predictions(["target_name1", "target_name2"]))
        {'target_name1': {'confidence': 1.0, 'value': 'feed'}, 'target_name2': {'confidence': 0.97, 'value': 'deed'}}
        """
        if not subset:
            return self.data.prediction
        for name in subset:
            if (
                not name in self.data.prediction
                or self.data.prediction[name] is None
            ):
                return {}
        return {name: self.data.prediction[name] for name in subset}
