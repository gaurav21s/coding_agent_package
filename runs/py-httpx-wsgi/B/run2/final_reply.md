To test a WSGI application in-process using `httpx`, you can use the `httpx.WSGITransport` class. This allows you to pass a standard WSGI application directly to an `httpx.Client`, enabling you to make requests to your application without needing to bind to a network port or start a separate server process.

The following program defines a simple WSGI application that returns "hello" with a 200 status code, configures an `httpx.WSGITransport` with that application, and uses an `httpx.Client` to perform a GET request.

```python
import httpx

def simple_wsgi_app(environ, start_response):
    """
    A minimal WSGI application that returns 'hello' with status 200.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'hello']

def main():
    # Create the WSGI transport using our application
    transport = httpx.WSGITransport(app=simple_wsgi_app)

    # Use the transport with an httpx.Client.
    # The base_url is required for the client to know where to route requests.
    with httpx.Client(transport=transport, base_url="http://testserver") as client:
        response = client.get("/")

        # Print the results
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    main()
```