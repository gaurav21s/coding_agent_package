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
