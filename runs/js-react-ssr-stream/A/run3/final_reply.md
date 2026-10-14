To achieve server-side streaming of React components in Node.js, we use the `renderToPipeableStream` method from `react-dom/server`. Since we are using plain JavaScript without JSX, we use `React.createElement`.

As of October 2026, `react` and `react-dom` are at version 19.x. The following code uses the standard Node.js `Writable` stream interface to pipe the output to `process.stdout`.

```javascript
import React from 'react';
import { renderToPipeableStream } from 'react-dom/server';

/**
 * A simple component represented as a function.
 * Using React.createElement instead of JSX.
 */
function ListComponent() {
  return React.createElement(
    'ul',
    null,
    React.createElement('li', null, 'Item 1'),
    React.createElement('li', null, 'Item 2'),
    React.createElement('li', null, 'Item 3')
  );
}

// Create the stream from the component
const stream = renderToPipeableStream(React.createElement(ListComponent), {
  onShellReady() {
    // Pipe the stream to stdout
    stream.pipe(process.stdout);
  },
  onAllReady() {
    // Print 'done' once the stream has finished
    process.stdout.write('\ndone\n');
  },
  onError(error) {
    console.error(error);
  }
});
```

### How to run:
1. Ensure you have `react` and `react-dom` installed:
   `npm install react react-dom`
2. Save the code above as `main.mjs`.
3. Run the program:
   `node main.mjs`

This script will output the HTML string of the `<ul>` list followed by the word "done" on a new line.