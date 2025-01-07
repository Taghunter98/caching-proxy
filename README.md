# Caching Proxy Server

A simple Python-based caching proxy server that forwards requests to an origin server and caches responses for subsequent requests. This tool is useful for reducing load on the origin server and improving response times for frequently accessed resources.

## Features

- Caches responses locally to serve repeated requests faster.
- Forwards uncached requests to the specified origin server.
- Supports HTTP/1.1 requests.
- Handles errors gracefully, including 404 and origin server connection failures.
- Configurable via command-line arguments.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Taghunter98/caching-proxy.git
   cd caching-proxy
   ```

2. **Set Up a Virtual Environment** (optional, but reccomended for Linux users):

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install Dependencies**:
   The script uses Python's standard library, so no additional dependencies are required.

## Usage

Run the server with the following command:

```bash
python3 caching-proxy.py --port <PORT> --origin <ORIGIN_URL>
```

- `--port`: The port number the proxy server will listen on (e.g., `2000`).
- `--origin`: The origin server's URL to forward uncached requests to (e.g., `http://dummyjson.com`).

### Example:

```bash
python3 caching-proxy.py --port 2000 --origin http://dummyjson.com
```

## How It Works

1. **Incoming Requests**:

   - The proxy server listens for incoming HTTP requests from clients.

2. **Cache Lookup**:

   - For each request, the server checks if the response is already cached.
   - If cached, the response is returned directly to the client.

3. **Forward to Origin**:

   - If the requested resource is not in the cache, the server forwards the request to the origin server.
   - The origin's response is cached and sent to the client.

4. **Error Handling**:
   - If the origin server is unreachable or returns an error, the client receives an appropriate error message.

## Testing

### From Local Machine

- Use a browser or `curl` to send requests to the proxy server:
  ```bash
  curl http://localhost:2000/products
  ```
- Observe cached responses for repeated requests.

### From Another Device

1. Bind the server to `0.0.0.0` in the script to allow external access.
2. Find your local IP address and use it to access the server, e.g., `http://192.168.1.10:2000/products`.

## Known Limitations

- Does not support HTTPS out of the box.
- Limited to GET requests for simplicity.
- Cache is stored in plain text files; consider enhancing it for production use.

## Future Enhancements

- Add HTTPS support.
- Implement cache eviction policies (e.g., LRU, time-based).
- Extend support to other HTTP methods like POST.
- Add multithreading for handling multiple requests concurrently.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
