# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Information on the software to evaluate is stored in a Repo instance.
"""
import os
import warnings
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncIterator

from .util.data import merge
from .log import LOGGER

LOGGER = LOGGER.getChild("repo")


class NoSuchFeature(KeyError):
    pass  # pragma: no cov


class RepoPrediction(dict):

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


class RepoData(object):

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    EXPORTED = ["src_url", "features", "prediction"]

    def __init__(
        self,
        *,
        src_url: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        prediction: Optional[RepoPrediction] = None,
        last_updated: Optional[datetime] = None,
    ) -> None:
        # If the repo is not evaluated or predicted then don't report out a new
        # value for last_updated
        self.last_updated_default = datetime.now()
        if src_url is None:
            src_url = ""
        if features is None:
            features = {}
        if prediction is None:
            prediction = RepoPrediction()
        if last_updated is None:
            last_updated = self.last_updated_default
        if isinstance(last_updated, str):
            last_updated = datetime.strptime(last_updated, self.DATE_FORMAT)
        self.src_url = src_url
        self.features = features
        self.prediction = RepoPrediction(**prediction)
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


class Repo(object):
    """
    Manages feature independent information and actions for a repo.
    """

    REPO_DATA = RepoData

    def __init__(
        self,
        src_url: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if data is None:
            data = {}
        if extra is None:
            extra = {}
        data["src_url"] = src_url
        if "extra" in data:
            # Prefer extra from init arguments to extra stored in data
            data["extra"].update(extra)
            extra = data["extra"]
            del data["extra"]
        self.data = self.REPO_DATA(**data)
        self.extra = extra

    def dict(self):
        # TODO(p2) Remove dict method in favor of export
        return self.export()

    def export(self):
        data = self.data.dict()
        data["extra"] = self.extra
        return data

    def __repr__(self):
        return str(self.dict())

    def __str__(self):
        if not self.data.prediction:
            confidence, value = (0.0, "Undetermined")
        else:
            confidence, value = (
                self.data.prediction.confidence,
                self.data.prediction.value,
            )
        header = "%-11s (%2.1f%% confidence) %s" % (
            value,
            100.0 * confidence,
            self.src_url,
        )
        if len(self.extra.keys()):
            header += " " + str(self.extra)
        return "\n".join(
            [header]
            + [
                ("%-30s%s" % (feature, str(results)))
                for feature, results in self.features().items()
            ]
        ).rstrip()

    def merge(self, repo: "Repo"):
        data = self.data.dict()
        merge(data, repo.data.dict())
        self.data = self.REPO_DATA(**data)
        self.extra.update(repo.extra)  # type: ignore

    @property
    def src_url(self) -> str:
        return self.data.src_url

    def evaluated(self, results: Dict[str, Any], overwrite=False):
        """
        Updates features with the result dict
        """
        if overwrite:
            self.data.features = results
        else:
            self.data.features.update(results)
        self.data.last_updated = datetime.now()
        LOGGER.info("Evaluated %s %r", self.data.src_url, self.data.features)

    def features(self, subset: List[str] = []) -> Dict[str, Any]:
        """
        Returns all features for the repo or the subset specified.
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
        Returns a feature of the repo.
        """
        if name not in self.data.features:
            raise NoSuchFeature(name)
        return self.data.features[name]

    def predicted(self, value: Any, confidence: float):
        """
        Set the prediction for this repo
        """
        self.data.prediction = RepoPrediction(
            value=value, confidence=float(confidence)
        )
        self.data.last_updated = datetime.now()

    def prediction(self) -> RepoPrediction:
        """
        Get the prediction for this repo
        """
        return self.data.prediction
