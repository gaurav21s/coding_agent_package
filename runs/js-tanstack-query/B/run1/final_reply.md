To implement this, we use `@tanstack/query-core`. We configure the `QueryClient` with `defaultOptions` to set `gcTime` (garbage collection time) to 5 minutes (300,000 ms) and `staleTime` to 60 seconds (60,000 ms).

We use `client.fetchQuery` to imperatively fetch the data. Since the second fetch occurs immediately after the first, it will be served from the cache because the data is still considered "fresh" (within the 60-second `staleTime`).

```javascript
import { QueryClient } from '@tanstack/query-core';

// 1. Initialize QueryClient with specified defaults
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

  // 2. First fetch
  const result1 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  // 3. Second fetch (should be cached)
  const result2 = await queryClient.fetchQuery({
    queryKey,
    queryFn: fetchTodo,
  });

  // 4. Print results
  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // 5. Clear client
  queryClient.clear();
}

run().catch(console.error);
```