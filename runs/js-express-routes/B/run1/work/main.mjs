import express from 'express';

const app = express();

// DELETE /users/:id route
app.delete('/users/:id', (req, res) => {
  res.status(204).send();
});

// GET /search route
app.get('/search', (req, res) => {
  res.json({ q: req.query.q });
});

// Catch-all route for any other GET path
app.get('*', (req, res) => {
  res.status(404).send('not found');
});

const server = app.listen(0, async () => {
  const port = server.address().port;
  const baseUrl = `http://localhost:${port}`;

  try {
    // 1. DELETE /users/7
    const res1 = await fetch(`${baseUrl}/users/7`, { method: 'DELETE' });
    console.log(`DELETE /users/7: ${res1.status}`);

    // 2. GET /search?q=x
    const res2 = await fetch(`${baseUrl}/search?q=x`);
    const body2 = await res2.json();
    console.log(`GET /search?q=x: ${res2.status}, ${JSON.stringify(body2)}`);

    // 3. GET /nope
    const res3 = await fetch(`${baseUrl}/nope`);
    const body3 = await res3.text();
    console.log(`GET /nope: ${res3.status}, ${body3}`);
  } catch (err) {
    console.error('Error during fetch:', err);
  } finally {
    server.close();
  }
});
