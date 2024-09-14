## Machine Learning

This is image is for both serving ML model recommendations, and training the ML models.

This is currently a rough implementation on the tensorflow recommenders. https://www.tensorflow.org/recommenders

Working on implementing LTR for a SOLR search engine, taking inspiration from here: https://github.com/airalcorn2/Solr-LTR

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

After adding the required .env values you can then run `python Controller.py`

### Build

```
docker-compose build ml
```

### Formatting

After the dependencies have been installed, you can use yapf for the auto formatting with the following:
```
yapf -i . --recursive --style='{indent_width: 2}'
```
