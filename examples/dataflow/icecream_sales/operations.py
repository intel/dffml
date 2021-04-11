import json
import pathlib

from dffml import (
    op,
    load,
    export,
    Definition,
    cached_download,
)


temperature_dataset_urls = {
    "Phoenix city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00023183-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1933&endbaseyear=2000",
        "expected_sha384_hash": "f26d3d8cb691f2c5544d05da35995329028cf04356f8018a94102701bc49edd34911a0a076eed376a11f1514ce06b277",
    },
    "Orlando city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00012815-tavg-all-2-2020-2021.json?base_prd=true&begbaseyear=1952&endbaseyear=2000",
        "expected_sha384_hash": "e239a9245188797da6c2b73a837785f075c462a8de6fce135a3db94c4155b586456263961c68ead2758f8185ef0a70c0",
    },
    "Miami city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00012839-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1948&endbaseyear=2000",
        "expected_sha384_hash": "797c5e1645b381c242fa1defcd0cd63549770a2e68481da9253bfc04e6ece826899d19112b52ae03e84bc7ad25d4063f",
    },
    "Portland city (pt.)": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00024229-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1938&endbaseyear=2000",
        "expected_sha384_hash": "a0f2a87bca37cfe7ea79a25d58d0280af1c4347360ab7bcadb3be4a71963ec234d14c763c12dafd9facf5fe75f3a9502",
    },
    "New York city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00094789-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1948&endbaseyear=2000",
        "expected_sha384_hash": "4e029455185fbed76e9e9bd71344dd424a3de767a4e0fc0439fbadc5cc8bfa203bbfa8e5545df8ac7812124d3d5674f0",
    },
    "Las Vegas city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00023169-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1948&endbaseyear=2000",
        "expected_sha384_hash": "d7082f31f97c56a36f579f6fd0d361caff0aa585dcadf3a63294d74bd31881517d7a0e970537993cb75c17ccba1ceb4e",
    },
    "Seattle city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00024233-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1948&endbaseyear=2000",
        "expected_sha384_hash": "d4c291ead4a5f4a15b7d4ef456b73e3754b4bbbff3614b56d7bdff4631d2af3205795cc39ca132091b413f95e56768c0",
    },
    "Chicago city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00094846-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1958&endbaseyear=2000",
        "expected_sha384_hash": "1ee80e616b70f16c193e565215f216a354324f58f12373502fb7763edb304af4bbd56d06c3c8bc0f0a23f7e7e85a5a0e",
    },
    "Buffalo city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USH00301012-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1958&endbaseyear=2000",
        "expected_sha384_hash": "8ffbaf046ac1b3538d1a825942beb1f1a5420d18fe69fce090f34167df78ea3c863202b520558ffd5bf99425ffd8b232",
    },
    "Salem city": {
        "url": "https://www.ncdc.noaa.gov/cag/city/time-series/USW00024232-tavg-all-1-2020-2021.json?base_prd=true&begbaseyear=1958&endbaseyear=2000",
        "expected_sha384_hash": "d1df691b45ea66be3329e31d5f7d84a583164c8293842490c8a32c46dd89bb776182ed4c4a0e51968b3bf60d76f1998b",
    },
}


population_dataset_urls = {
    "Arizona": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_4.csv",
        "expected_sha384_hash": "56f6dc515f42e584df8f2806dea2fc0f955916bc9b697975b5bb62a4efd5efa1065738a56f049053164ecd150cf84f5c",
    },
    "Florida": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_12.csv",
        "expected_sha384_hash": "969cc1abd2f3f30a9208277fcb760d4cc9e9deb67a605ca0017daf784782d5180a1e2d5c6982a84783ec310c3dde13d2",
    },
    "Oregon": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_41.csv",
        "expected_sha384_hash": "c11bb1be135eb9f2521e6397339c10c87baae4669aab46198f87716cc652a2f8c85a96c477aabe7e11240d5049b1149a",
    },
    "New York": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_36.csv",
        "expected_sha384_hash": "cd77a3c4ab0099a8353e5118e82c184622274484328883f86eae59755a6a81ad039c5c55339f730a990b0bf412acc6c2",
    },
    "Nevada": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_32.csv",
        "expected_sha384_hash": "d8518c388107483dc0da65e33769ea8e8d7983ce17f79f7020201cf3754cd4a59b9ce57e479b4c1208a46c2dd8be4fde",
    },
    "Washington": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_53.csv",
        "expected_sha384_hash": "b426810c8438585c67057c5073281fce6b20d6bf013370256d6dbdcc4ad0b92c7d673c1e7d6e2a1d14e59f7bbc6599ad",
    },
    "Illinois": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_17.csv",
        "expected_sha384_hash": "a55edf7f31ccdc792d183bb0c1dccbc55f6cfb5d518502e3fc5278d230a0174a741ae625d2b00e650dc1d8cd39f2e989",
    },
}


temperature_def = Definition(name="temperature", primitive="generic")
population_def = Definition(name="population", primitive="generic")


@op(outputs={"temperature": temperature_def})
async def lookup_temperature(self, city: str, month: int):
    if city not in temperature_dataset_urls:
        raise Exception(f"City: {city} not found in dataset")

    cache_dir = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "temperature")
        .expanduser()
        .resolve()
    )

    filepath = await cached_download(
        temperature_dataset_urls[city]["url"],
        cache_dir / f"{city}.json",
        temperature_dataset_urls[city]["expected_sha384_hash"],
    )
    dataset = json.loads(pathlib.Path(filepath).read_text())
    temperature = dataset["data"][
        f"20200{month}" if month < 10 else f"2020{month}"
    ]["value"]
    return {"temperature": float(temperature)}


@op(outputs={"population": population_def})
async def lookup_population(self, city: str, state: str):
    if city not in temperature_dataset_urls:
        raise Exception(f"City: {city} not found in dataset")

    if state not in population_dataset_urls:
        raise Exception(f"State: {state} not found in dataset")

    cache_dir = (
        pathlib.Path("~", ".cache", "dffml", "datasets", "population")
        .expanduser()
        .resolve()
    )

    filepath = await cached_download(
        population_dataset_urls[state]["url"],
        cache_dir / f"{state}.csv",
        population_dataset_urls[state]["expected_sha384_hash"],
    )
    async for record in load(filepath):
        if export(record)["features"]["NAME"] == city:
            population = export(record)["features"]["POPESTIMATE2019"]
            yield {"population": population}
