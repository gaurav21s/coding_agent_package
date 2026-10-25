To create this application, we use `express` version 5.x. Following the migration guide, we use `app.delete()` for the DELETE route, `res.status(code).json()` for JSON responses, and the `/*splat` syntax for the wildcard route.

```javascript
import express from 'express';

const app = express();

// DELETE /users/:id route
app.delete('/users/:id', (req, res) => {
  res.status(204).send();
});

// GET /search route
app.get('/search', (req, res) => {
  res.status(200).json({ q: req.query.q });
});

// Catch-all route using /*splat
app.get('/*splat', (req, res) => {
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
    console.error(err);
  } finally {
    server.close();
  }
});
```