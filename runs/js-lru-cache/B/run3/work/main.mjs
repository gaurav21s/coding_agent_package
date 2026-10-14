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
