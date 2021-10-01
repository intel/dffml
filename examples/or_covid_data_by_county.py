import asyncio
import pathlib
import datetime
from typing import AsyncIterator, Type

from dffml import *

import joblib
import pandas
from fbprophet import Prophet


@config
class FBProphetModelConfig:
    date: Feature = field("Name of feature containing date value")
    predict: Feature = field("Label or the value to be predicted")
    location: pathlib.Path = field("Location where state should be saved")


@entrypoint("fbprophet")
class FBProphetModel(SimpleModel):
    # The configuration class needs to be set as the CONFIG property
    CONFIG: Type = FBProphetModelConfig

    def __init__(self, config) -> None:
        super().__init__(config)
        # The saved model
        self.saved = None
        self.saved_filepath = pathlib.Path(
            self.config.location, "model.joblib"
        )
        # Load saved model if it exists
        if self.saved_filepath.is_file():
            self.saved = joblib.load(str(self.saved_filepath))

    async def train(self, sources: SourcesContext) -> None:
        # Create a pandas DataFrame from the records with the features we care
        # about. Prophet wants each row in the DataFrame to have two features,
        # ds for the date, and y for the label (the value to predict).
        df = pandas.DataFrame.from_records(
            [
                {
                    "ds": record.feature(self.config.date.name),
                    "y": record.feature(self.config.predict.name),
                }
                async for record in sources.with_features(
                    [self.config.date.name, self.config.predict.name]
                )
            ]
        )
        # Use self.logger to report how many records are being used for training
        self.logger.debug("Number of training records: %d", len(df))
        # Create an instance of the Prophet model class
        self.saved = Prophet()
        # Train the model
        self.saved.fit(df)
        # Save the model
        joblib.dump(self.saved, str(self.saved_filepath))

    async def accuracy(self, sources: SourcesContext) -> Accuracy:
        # We're not going to calculate accuracy in the example
        raise NotImplementedError()

    async def predict(self, sources: SourcesContext) -> AsyncIterator[Record]:
        # Ensure there is a saved model
        if not self.saved:
            raise ModelNotTrained("Train the model before making predictions")
        # Load all the records into memory for the sake of speed
        records = [
            record
            async for record in sources.with_features([self.config.date.name])
        ]
        # Create a pandas DataFrame from the records that have a date feature
        future = pandas.DataFrame.from_records(
            [
                {"ds": record.feature(self.config.date.name)}
                for record in records
            ]
        )
        # Ask the model for predictions
        for record, value in zip(
            records, self.saved.predict(future).itertuples()
        ):
            # Set the predicted value
            # TODO do not use nan for confidence
            record.predicted(
                self.config.predict.name, value.yhat, float("nan")
            )
            # Yield the record
            yield record


async def main():
    # DFFML has a function to download files and validate their contents using
    # SHA 384 hashes. If you need to download files from an http:// site, you need
    # to add the following to the call to cached_download()
    #   protocol_allowlist=["https://", "http://"]
    training_file = await cached_download(
        "https://github.com/intel/dffml/files/5773999/COVID.Oregon.Counties.Train.Clean.to.2020-10-24.csv.gz",
        "training.csv.gz",
        "af9536ab41580e04dd72b1285f6b2b703977aee5b95b80422bbe7cc11262297da265e6c0e333bfc1faa7b4f263f5496e",
    )
    test_file = await cached_download(
        "https://github.com/intel/dffml/files/5773998/COVID.Oregon.Counties.Test.Clean.2020-10-25.to.2020-10-31.csv.gz",
        "test.csv.gz",
        "10ee8bcf06a511019f98c3e0e40f315585b2ed84d4a736f743567861d72438afcb7914f117e16640800959324f0f518d",
    )

    # Load the training data
    training_data = [record async for record in load(training_file)]

    # Load the test data
    test_data = [record async for record in load(test_file)]

    # Deaths and cases should have a relatively linear relationship. The cases
    # to deaths model will be trained to predict the number of deaths given the
    # number of cases. Try swapping the SLRModel for another model on the
    # plugins page.
    cases_to_deaths_model = SLRModel(
        features=Features(Feature("cases", int)),
        predict=Feature("deaths", int),
        location="cases_to_deaths.model",
    )

    # Train the model to learn the relationship between cases and deaths
    await train(cases_to_deaths_model, *training_data)

    # Find the set of counties by looking through all the training data and
    # recording each county seen
    counties = set([record.feature("county") for record in training_data])

    # We want to forecast the number of cases by county. We'll train a
    # forecasting model on past data to predict the number of cases given the
    # date for the given county.
    date_to_cases_models = {
        county: FBProphetModel(
            date=Feature("date", str),
            predict=Feature("cases", int),
            location=f"date_to_cases.{county}.model",
        )
        for county in counties
    }

    # Group training data by county
    training_data_by_county = {county: [] for county in counties}
    for record in training_data:
        training_data_by_county[record.feature("county")].append(record)

    # Group test data by county
    test_data_by_county = {county: [] for county in counties}
    for record in test_data:
        test_data_by_county[record.feature("county")].append(record)

    # Get today's date
    todays_date = datetime.datetime.now()

    for county, model in date_to_cases_models.items():
        # Train a model for each county
        await train(model, *training_data_by_county[county])
        # We want predictions for the test data for this county
        want_predictions = test_data_by_county[county]
        # We also want to ask for today through four days from now
        prediction_dates = [
            (todays_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(0, 5)
        ]
        # We append those records to the set of records we want predictions for
        want_predictions += [
            Record(
                key=date, data={"features": {"county": county, "date": date}}
            )
            for date in prediction_dates
        ]
        # Predict the number of cases for the county
        async for record in predict(
            model, *want_predictions, keep_record=True
        ):
            # Get predicted value for cases
            predicted_cases = record.prediction("cases")["value"]
            # Report actual value for cases if we have it
            actual_cases = "Actual Cases Unknown"
            features = record.features()
            if "cases" in features:
                actual_cases = features["cases"]
            else:
                # If we don't have an actual value for cases set the cases
                # feature to the predicted value so that we can feed it into the
                # next model for a number of deaths prediction
                record.evaluated({"cases": predicted_cases})
            # Use the cases to deaths model to predict the deaths. It's a loop
            # but we're only feeding it the one record from the loop we're in.
            async for record in predict(
                cases_to_deaths_model, record, keep_record=True
            ):
                # Get predicted value for deaths
                predicted_deaths = record.prediction("deaths")["value"]
                # Report actual value for deaths if we have it
                actual_deaths = "Actual Deaths Unknown"
                if "deaths" in features:
                    actual_deaths = features["deaths"]
                # Print out predictions
                print("---------------------------------------")
                print(f'county:           : {features["county"]}')
                print(f'date:             : {features["date"]}')
                print(f"predicted_cases   : {predicted_cases}")
                print(f"actual_cases      : {actual_cases}")
                print(f"predicted_deaths  : {predicted_deaths}")
                print(f"actual_deaths     : {actual_deaths}")


if __name__ == "__main__":
    asyncio.run(main())
