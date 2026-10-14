import httpx

def simple_wsgi_app(environ, start_response):
    """A simple WSGI application that returns 'hello'."""
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'hello']

def main():
    # Create the WSGI transport using the app
    transport = httpx.WSGITransport(app=simple_wsgi_app)

    # Use the transport in a synchronous httpx Client
    # The base_url is required for the transport to route requests correctly
    with httpx.Client(transport=transport, base_url="http://testserver") as client:
        response = client.get("/")

        # Print the results
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    main()
