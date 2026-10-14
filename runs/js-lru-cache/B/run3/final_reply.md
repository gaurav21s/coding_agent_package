To implement the requested functionality using `lru-cache`, we need to configure the cache with `max: 100` and `ttl: 50`. Since `lru-cache` does not automatically purge expired items in the background by default (it purges them upon access), we must enable `ttlAutopurge: true` to ensure items are removed 50 ms after they are set, even if they are not accessed.

Here is the `main.mjs` file:

```javascript
import { LRUCache } from 'lru-cache';

// Initialize cache with max 100 entries and 50ms TTL.
// ttlAutopurge: true ensures items are removed automatically after the TTL.
const cache = new LRUCache({
  max: 100,
  ttl: 50,
  ttlAutopurge: true,
});

async function run() {
  console.log(`Initial cache size: ${cache.size}`);

  // Set two keys
  cache.set('key1', 'value1');
  cache.set('key2', 'value2');
  console.log(`Cache size after setting two keys: ${cache.size}`);

  // Remove one key explicitly
  cache.delete('key1');
  console.log(`Cache size after deleting 'key1': ${cache.size}`);

  // Wait 80ms (longer than the 50ms TTL)
  await new Promise((resolve) => setTimeout(resolve, 80));

  // Check the other key
  console.log(`Cache size after waiting 80ms: ${cache.size}`);
  console.log(`'key2' exists: ${cache.has('key2')}`);

  // Empty the cache completely
  cache.clear();
  console.log(`Cache size after clearing: ${cache.size}`);
}

run().catch(console.error);
```

### How to run:
1. Ensure you have `lru-cache` installed:
   ```bash
   npm install lru-cache
   ```
2. Save the code above as `main.mjs`.
3. Run the program:
   ```bash
   node main.mjs
   ```