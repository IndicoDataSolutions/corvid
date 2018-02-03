#!/bin/bash

(docker build --tag results_extraction .) &&
(docker run --rm results_extraction pytest tests/) &&
(docker run --rm results_extraction pylint --disable=R,C,W extract_empirical_results)
