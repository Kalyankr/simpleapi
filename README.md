# SimpleAPI

SimpleAPI is Flask like API framework (Practice) for building RESTful web services in Python.

## Features

- Lightweight and fast
- Easy to set up and use
- Supports JSON responses

## Installation

To install SimpleAPI, use pip:

```bash
pip install simpleapi
```

## Usage

Here is an example of how to use SimpleAPI to create a simple web service:

```python
from simpleapi import SimpleAPI

app = SimpleAPI()

@app.get('/hello')
def hello_world(request):
    return {'message': 'Hello, world!'}

if __name__ == '__main__':
    app.run()
```

## Running the Example

Save the above code to a file, for example `app.py`, and run it:

```bash
python app.py
```

You can then access the API at `http://localhost:8000/hello` and you should see the following JSON response:

```json
{
    "message": "Hello, world!"
}
```

## Documentation

For more detailed documentation, please refer to the [official documentation](https://example.com/simpleapi-docs).

## License

SimpleAPI is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.