To implement this using `@tanstack/query-core` (v5.59.1 as of today), we configure the `QueryClient` with `defaultOptions`. We use `gcTime` (formerly `cacheTime`) for garbage collection and `staleTime` for freshness.

Since we are in a Node.js environment, we use the `fetchQuery` method. To track how many times the fetch function runs, we use a simple counter variable.

```javascript
import { QueryClient } from '@tanstack/query-core';

// Initialize the QueryClient with the requested settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 5 * 60 * 1000, // 5 minutes
      staleTime: 60 * 1000,  // 60 seconds
    },
  },
});

let fetchCount = 0;

const fetchTodo = async () => {
  fetchCount++;
  return { id: 1, title: 'x' };
};

async function run() {
  const queryKey = ['todo', 1];

  // First fetch: Should trigger the fetch function
  const result1 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  // Second fetch: Should return cached data immediately
  const result2 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // Clear the client
  queryClient.clear();
  console.log('Client cleared.');
}

run().catch(console.error);
```

### Explanation:
1.  **`gcTime`**: Set to `5 * 60 * 1000` ms (5 minutes). This controls how long unused data remains in memory.
2.  **`staleTime`**: Set to `60 * 1000` ms (60 seconds). Because the second fetch happens immediately after the first, the data is still considered "fresh," so `fetchQuery` returns the cached result without re-running the `queryFn`.
3.  **`fetchCount`**: This variable increments inside the `fetchTodo` function. It will be `1` at the end of the script, confirming the second call was served from the cache.
4.  **`queryClient.clear()`**: Removes all queries from the cache as requested.

```javascript
import { QueryClient } from '@tanstack/query-core';

// Initialize the QueryClient with the requested settings
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 5 * 60 * 1000, // 5 minutes
      staleTime: 60 * 1000,  // 60 seconds
    },
  },
});

let fetchCount = 0;

const fetchTodo = async () => {
  fetchCount++;
  return { id: 1, title: 'x' };
};

async function run() {
  const queryKey = ['todo', 1];

  // First fetch: Should trigger the fetch function
  const result1 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  // Second fetch: Should return cached data immediately
  const result2 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // Clear the client
  queryClient.clear();
  console.log('Client cleared.');
}

run().catch(console.error);
```