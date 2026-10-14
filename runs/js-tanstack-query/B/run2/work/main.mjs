import { QueryClient } from '@tanstack/query-core';

// 1. Configure QueryClient
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

  console.log('Result 1:', result1);
  console.log('Result 2:', result2);
  console.log('Fetch function ran times:', fetchCount);

  // 4. Clear the client
  queryClient.clear();
  console.log('Client cleared.');
}

run().catch(console.error);
