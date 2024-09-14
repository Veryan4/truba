## Core Api

This service manages all back-end communication. There is a back-end facing (core.py), front-end facing (coreui.py), cronjob'd (push.py), and async (worker.py) copy of the same image.

### Running
 
Make sure to copy the shared interfaces before running
```
yes | cp -r -f ../shared .
```

You then need to install the dependencies
```
pip install -r requirements.txt
```
You then need to generate the shared models
```
datamodel-codegen  --input ../schemas/AllTypes.yaml --aliases ../schemas/aliases.json --output project_types.py
```

After adding the required .env values, you can then run one of the services with `python <name-of-service>` 

Available services: core.py, coreui.py, socket.py, push.py, or worker.py

### Tests

You then need to install the dependencies
```
pip install -r requirements-for-tests.txt
```

Then run the tests with 
```
pytest tests
```

### Build

```
docker-compose build core
```

### Formatting

After the dependencies have been installed, you can use yapf for the auto formatting with the following:
```
yapf -i . --recursive --style='{indent_width: 2}'
```
