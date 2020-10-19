python -m pytest --cov=pxtrade --cov-report=html --doctest-modules
flake8 pxtrade
black --check pxtrade
flake8 tests
black --check tests
