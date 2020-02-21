# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Information on the software to evaluate is stored in a Repo instance.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

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
    EXPORTED = ["key", "features", "prediction"]

    def __init__(
        self,
        *,
        key: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
        prediction: Optional[Dict[str, Any]] = None,
        last_updated: Optional[datetime] = None,
    ) -> None:
        # If the repo is not evaluated or predicted then don't report out a new
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
            prediction[_key] = RepoPrediction(**_val)
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


class Repo(object):
    """
    Manages feature independent information and actions for a repo.
    """

    REPO_DATA = RepoData

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
        header = self.key
        if len(self.extra.keys()):
            header += " " + str(self.extra)

        return "\n".join(
            [header]
            + [
                ("%-30s%s" % (feature, str(results)))
                for feature, results in self.features().items()
            ]
            + ["Predictions"]
            + (
                [
                    (
                        "%-30s\n\tvalue:%s, confidence:%s"
                        % (
                            pred,
                            str(conf_val["value"]),
                            str(conf_val["confidence"]),
                        )
                    )
                    for pred, conf_val in self.data.prediction.items()
                ]
                if self.data.prediction
                else ["Undetermined"]
            )
        ).rstrip()

    def merge(self, repo: "Repo"):
        data = self.data.dict()
        merge(data, repo.data.dict())
        self.data = self.REPO_DATA(**data)
        self.extra.update(repo.extra)  # type: ignore

    @property
    def key(self) -> str:
        return self.data.key

    def evaluated(self, results: Dict[str, Any], overwrite=False):
        """
        Updates features with the result dict
        """
        if overwrite:
            self.data.features = results
        else:
            self.data.features.update(results)
        self.data.last_updated = datetime.now()
        LOGGER.info("Evaluated %s %r", self.data.key, self.data.features)

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

    def predicted(self, target: str, value: Any, confidence: float):
        """
        Set the prediction for this repo
        """
        self.data.prediction[target] = RepoPrediction(
            value=value, confidence=float(confidence)
        )
        self.data.last_updated = datetime.now()

    def prediction(self, target: str) -> RepoPrediction:
        """
        Get the prediction for this repo
        """
        return self.data.prediction[target]

    def predictions(self, subset: List[str] = []) -> Dict[str, Any]:
        if not subset:
            return self.data.prediction
        for name in subset:
            if (
                not name in self.data.prediction
                or self.data.prediction[name] is None
            ):
                return {}
        return {name: self.data.prediction[name] for name in subset}
