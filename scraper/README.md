## Core Api

This service manages all back-end communication. There is a back-end facing (Controller.py), front-end facing (UiContrller.py), and async (Worker.py) copy of the same image.

## List of scraped sources

A list of sources that are used can be found [here](https://airtable.com/invite/l?inviteId=invjDxkD4T0H9ypwa&inviteToken=254370034c8d6efff4123af230402ed5f6d03c77492f3bba8bfc7689c5dc32fb&utm_source=email)

When adding a new source to the list, a scraper class for the source must also be created under the sources dir.

### Running
 
Make sure to copy the shared interfaces before running
```
yes | cp -r -f ../shared .
```

You then need to install the dependencies
```
pip install -r requirements.txt
```

After adding the required .env values you can then run `python Scraper.py`

### Tests

You then need to install the dependencies
```
pip install -r requirements-for-tests.txt
```

Then run the tests with 
```
pytest tests
```

If contributing, note that unit-tests are not required for the `sources` directory, since these classes are subject to frequent changes.

### Build

```
docker-compose build scraper
```

### Formatting

After the dependencies have been installed, you can use yapf for the auto formatting with the following:
```
yapf -i . --recursive --style='{indent_width: 2}'
```
