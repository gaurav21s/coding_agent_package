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
