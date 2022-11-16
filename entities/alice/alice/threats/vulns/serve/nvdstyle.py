import json
import math
import pathlib
import logging
import datetime
import unittest
import http.server
import urllib.parse
import urllib.request


SINGLE_CVE_ITEM = {
    "configurations": {"CVE_data_version": "4.0", "nodes": []},
    "cve": {
        "CVE_data_meta": {
            "ASSIGNER": "security-advisories@github.com",
            "ID": "CVE-2022-41917",
        },
        "data_format": "MITRE",
        "data_type": "CVE",
        "data_version": "4.0",
        "description": {
            "description_data": [
                {
                    "lang": "en",
                    "value": "OpenSearch is a community-driven, open source fork of Elasticsearch and Kibana. OpenSearch allows users to specify a local file when defining text analyzers to process data for text analysis. An issue in the implementation of this feature allows certain specially crafted queries to return a response containing the first line of text from arbitrary files. The list of potentially impacted files is limited to text files with read permissions allowed in the Java Security Manager policy configuration. OpenSearch version 1.3.7 and 2.4.0 contain a fix for this issue. Users are advised to upgrade. There are no known workarounds for this issue.",
                }
            ]
        },
        "problemtype": {"problemtype_data": [{"description": []}]},
        "references": {
            "reference_data": [
                {
                    "name": "https://github.com/opensearch-project/OpenSearch/security/advisories/GHSA-w3rx-m34v-wrqx",
                    "refsource": "CONFIRM",
                    "tags": [],
                    "url": "https://github.com/opensearch-project/OpenSearch/security/advisories/GHSA-w3rx-m34v-wrqx",
                },
                {
                    "name": "https://github.com/opensearch-project/OpenSearch/commit/6d20423f5920745463b1abc5f1daf6a786c41aa0",
                    "refsource": "MISC",
                    "tags": [],
                    "url": "https://github.com/opensearch-project/OpenSearch/commit/6d20423f5920745463b1abc5f1daf6a786c41aa0",
                },
            ]
        },
    },
    "impact": {},
    "lastModifiedDate": "2022-11-16T00:15Z",
    "publishedDate": "2022-11-16T00:15Z",
}
ALL_CVE_ITEMS = [SINGLE_CVE_ITEM] * 10


def helper_current_time_in_nist_nvd_format():
    # TODO Convert to UTC
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%MZ")


class NVDStyleHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        logger = logging.getLogger("alice.emulate.nvd.api")
        client_path_parsed = urllib.parse.urlparse(self.path)
        client_query_string = urllib.parse.parse_qs(client_path_parsed.query)
        # Set contents if unkown
        contents = json.dumps({"error": True, "message": "Cause unknown"}).encode()
        # Check if we are serving stats or not
        logger.debug(client_query_string)
        # Get values of applicable query strings
        request_stats = (
            client_query_string.get("reporttype", [False])[0] == "countsbystatus"
        )
        start_index = int(client_query_string.get("startIndex", ["-1"])[0])
        results_per_page = int(client_query_string.get("resultsPerPage", ["-1"])[0])
        if request_stats:
            # Serving stats
            logger.debug("Serving stats...")
            # TODO Update counts from operations which query Alice Stream of
            # Consciousness and run in EDEN.
            results = {
                # TODO FIXME Use correct timezone or convert to UTC
                "created": helper_current_time_in_nist_nvd_format()[:-1] + ".000+00:00",
                "dailyCounts": None,
                "error": None,
                "grid": None,
                "inVsOutCounts": None,
                "message": None,
                "metric": None,
                "params": None,
                "remainingVulnCounts": None,
                "title": None,
                "userActivityCountsMap": None,
                "vulnPeriodicCounts": None,
                "vulnsByScoreCounts": None,
                "vulnsByStatusCounts": [
                    {
                        "count": 0,
                        "description": "All CVEs that have been modified by the submission source after analysis and have not yet be re-analyzed.",
                        "endDate": None,
                        "name": "Modified",
                        "startDate": None,
                    },
                    {
                        "count": 0,
                        "description": "All CVEs that have been rejected by the submission source.",
                        "endDate": None,
                        "name": "Rejected",
                        "startDate": None,
                    },
                    {
                        "count": 0,
                        "description": "All CVEs waiting for acceptance.",
                        "endDate": None,
                        "name": "Received",
                        "startDate": None,
                    },
                    {
                        "count": len(ALL_CVE_ITEMS),
                        "description": "All CVEs known by service.",
                        "endDate": None,
                        "name": "Total",
                        "startDate": None,
                    },
                    {
                        "count": 0,
                        # "description": "All CVEs currently being analyzed by Alice ;) aka active CI/CD jobs.",
                        "description": "All CVEs currently being analyzed.",
                        "endDate": None,
                        "name": "Undergoing Analysis",
                        "startDate": None,
                    },
                    {
                        "count": 0,
                        "description": "All CVEs in queue for analysis.",
                        "endDate": None,
                        "name": "Awaiting Analysis",
                        "startDate": None,
                    },
                ],
                "xAxisTicks": None,
            }
            contents = json.dumps(results).encode()
        elif start_index == 0 and results_per_page == 1:
            # TODO Remove this special case, should be handled by feed.
            logger.debug(
                "Serving validate NVD API: start_index: %d results_per_page: %d...",
                start_index,
                results_per_page,
            )
            results = {
                "result": {
                    "CVE_Items": [
                        SINGLE_CVE_ITEM,
                    ],
                    "CVE_data_timestamp": helper_current_time_in_nist_nvd_format(),
                    # TODO VEX?
                    "CVE_data_format": "MITRE",
                    "CVE_data_type": "CVE",
                    "CVE_data_version": "4.0",
                },
                "resultsPerPage": 1,
                "startIndex": 0,
                "totalResults": len(ALL_CVE_ITEMS),
            }
            logger.debug(
                "Serving validate: results: %r",
                results,
            )
            contents = json.dumps(results).encode()
        elif start_index >= 0 and results_per_page > 0:
            # TODO Configurable cap on number of results per page
            if results_per_page > 40000:
                results_per_page = 40000
            # Reference: https://gist.github.com/pdxjohnny/47a6ddcd122a8f693ef346153708525a#file-pagination-py-L62-L65
            items = ALL_CVE_ITEMS
            total = len(ALL_CVE_ITEMS)
            logger.debug(
                "Serving feed: start_index: %d results_per_page: %d...",
                start_index,
                results_per_page,
            )
            # NVD starts at 0 but our logic started at 1
            # TODO Update data set iteration logic to base off 0 as start index
            # TODO Use DFFML source? Use runnning dataflow ctx, results.
            # Turn ctx into event for https://github.com/intel/dffml/issues/919
            start_index += 1
            results = {
                "result": {
                    "CVE_Items": items[
                        ((start_index - 1) * results_per_page) : (
                            (start_index - 1) * results_per_page
                        )
                        + results_per_page
                    ],
                    "CVE_data_timestamp": helper_current_time_in_nist_nvd_format(),
                    # TODO VEX?
                    "CVE_data_format": "MITRE",
                    "CVE_data_type": "CVE",
                    "CVE_data_version": "4.0",
                },
                "resultsPerPage": results_per_page,
                "startIndex": start_index,
                "totalResults": total,
            }
            # Feed example
            # https://gist.github.com/pdxjohnny/599b453dffc799f1c4dd8d8024b0f60e
            #   "resultsPerPage": 2000,
            #   "startIndex": 0,
            #   "totalResults": 3506
            logger.debug(
                "Serving feed with %d results",
                len(results["result"]["CVE_Items"]),
            )
            # Serving feed
            contents = json.dumps(results).encode()
        else:
            logger.debug(
                "Not sure what to do: start_index: %d results_per_page: %d",
                start_index,
                results_per_page,
            )
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", len(contents))
        self.end_headers()
        self.wfile.write(contents)


def main():
    import sys
    import httptest

    with httptest.Server(TestHTTPServer) as ts:
        with urllib.request.urlopen(ts.url()) as f:
            print(ts.url())
            sys.stdout.buffer.flush()
            input()


if __name__ == "__main__":
    main()
