#!/bin/bash
rm -r build/ dist/ kucoin_websocket/kucoin_websocket.egg-info
python3 -m pip install --upgrade setuptools wheel           # upgrade setuptools and wheel
python3 setup.py sdist bdist_wheel                          # build source and wheel distributions
python3 -m pip install --upgrade twine                      # upgrade twine
python3 -m twine upload dist/*                              # upload distributions to PyPI