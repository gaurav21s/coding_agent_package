To implement this, we use the `lru-cache` package (version 11.0.2 as of October 2026). The library uses the `ttl` option for expiration and the `max` option for capacity. Since `lru-cache` handles expiration lazily (checking on access) or via internal timers if configured, we use `ttlAutopurge: true` to ensure entries are removed automatically after the duration.

Here is the `main.mjs` file:

```javascript
import { LRUCache } from 'lru-cache';

// Initialize cache with max 100 entries and 50ms TTL
const cache = new LRUCache({
  max: 100,
  ttl: 50,
  ttlAutopurge: true,
});

async function run() {
  console.log(`Initial size: ${cache.size}`);

  // 1. Set two keys
  cache.set('key1', 'value1');
  cache.set('key2', 'value2');
  console.log(`Size after setting two keys: ${cache.size}`);

  // 2. Remove one explicitly
  cache.delete('key1');
  console.log(`Size after deleting key1: ${cache.size}`);

  // 3. Wait 80ms (longer than the 50ms TTL)
  await new Promise((resolve) => setTimeout(resolve, 80));
  
  // Note: ttlAutopurge handles the cleanup. 
  // We check size after the timeout.
  console.log(`Size after waiting 80ms: ${cache.size}`);

  // 4. Empty the cache completely
  cache.clear();
  console.log(`Size after clearing: ${cache.size}`);
}

run().catch(console.error);
```

### How to run:
1. Ensure you have the package installed:
   ```bash
   npm install lru-cache
   ```
2. Save the code above as `main.mjs`.
3. Run the program:
   ```bash
   node main.mjs
   ```

### Explanation:
*   **`ttl: 50`**: Sets the time-to-live for entries to 50 milliseconds.
*   **`ttlAutopurge: true`**: This is crucial; it ensures that the cache uses an internal `setInterval` to purge expired items, rather than waiting for a manual `get` call to trigger the expiration check.
*   **`cache.size`**: Returns the current number of items in the cache.
*   **`await new Promise(...)`**: Used to pause execution to allow the TTL timer to expire.