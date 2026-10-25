To implement this using `@tanstack/query-core` v5, we configure the `QueryClient` with `gcTime` (formerly `cacheTime`) set to 5 minutes (300,000ms) and `staleTime` set to 60 seconds (60,000ms). We use the `fetchQuery` method (which is the standard way to imperatively fetch data in v5) to retrieve the data.

Save the following code as `main.mjs`:

```javascript
import { QueryClient } from '@tanstack/query-core';

// Initialize QueryClient with specified garbage collection and freshness settings
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

  // First fetch: should trigger the fetch function
  const result1 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  // Second fetch: should return cached data (staleTime is 60s)
  const result2 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // Clear the client
  queryClient.clear();
}

run().catch(console.error);
```

### How to run:
1. Ensure you have initialized a project and installed the dependency:
   `npm install @tanstack/query-core`
2. Run the script:
   `node main.mjs`

### Explanation:
*   **`gcTime`**: Set to `300000` (5 minutes). This controls how long unused data remains in memory.
*   **`staleTime`**: Set to `60000` (60 seconds). Because the second `fetchQuery` occurs immediately, the data is considered "fresh," and TanStack Query returns the cached result without re-executing the `queryFn`.
*   **`fetchCount`**: This variable increments only during the first call, confirming that the second call was served from the cache.
*   **`queryClient.clear()`**: Clears all queries from the cache as requested.