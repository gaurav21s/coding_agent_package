To implement this using `@tanstack/query-core` (v5), we configure the `QueryClient` with `gcTime` (formerly `cacheTime`) set to 5 minutes (300,000ms) and `staleTime` set to 60 seconds (60,000ms). We use `queryClient.fetchQuery` to imperatively fetch the data.

Ensure you have installed the package: `npm install @tanstack/query-core`.

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

  // Second fetch: should return cached data (fetchCount should remain 1)
  const result2 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // Clear the client
  queryClient.removeQueries({ queryKey });
  console.log('Client cleared.');
}

run().catch(console.error);
```