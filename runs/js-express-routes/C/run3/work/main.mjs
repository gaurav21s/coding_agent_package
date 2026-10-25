import express from 'express';

const app = express();

// DELETE /users/:id
app.delete('/users/:id', (req, res) => {
  res.sendStatus(204);
});

// GET /search
app.get('/search', (req, res) => {
  res.status(200).json({ q: req.query.q });
});

// Catch-all route for GET requests
app.get('/*', (req, res) => {
  res.status(404).send('not found');
});

const server = app.listen(0, async () => {
  const port = server.address().port;
  const baseUrl = `http://localhost:${port}`;

  const requests = [
    { method: 'DELETE', url: `${baseUrl}/users/7` },
    { method: 'GET', url: `${baseUrl}/search?q=x` },
    { method: 'GET', url: `${baseUrl}/nope` }
  ];

  for (const req of requests) {
    const response = await fetch(req.url, { method: req.method });
    const body = await response.text();
    console.log(`Request: ${req.method} ${req.url}`);
    console.log(`Status: ${response.status}`);
    console.log(`Body: ${body || '(empty)'}`);
    console.log('---');
  }

  server.close();
});
