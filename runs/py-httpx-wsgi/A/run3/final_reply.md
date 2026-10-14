To test a WSGI application in-process using `httpx`, we use the `httpx.Client` with a custom `transport`. The `httpx.WSGITransport` class allows us to pass a WSGI application directly, which handles the request-response cycle without opening a network socket.

As of October 2026, `httpx` remains the standard for this approach. The following code defines a simple WSGI application and uses `httpx.WSGITransport` to execute the request in-process.

```python
import httpx

def simple_wsgi_app(environ, start_response):
    """
    A minimal WSGI application that returns 'hello' with a 200 OK status.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'hello']

def main():
    # Create a transport that routes requests to the WSGI app
    transport = httpx.WSGITransport(app=simple_wsgi_app)

    # Use the synchronous client with the custom transport
    with httpx.Client(transport=transport, base_url="http://testserver") as client:
        response = client.get("/")

        # Print the results
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    main()
```