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
