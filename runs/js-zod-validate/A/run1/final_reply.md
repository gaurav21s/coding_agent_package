To implement this using the latest version of `zod` (v3.24.1 as of October 2026), we will use standard ES module syntax.

### Prerequisites
Ensure you have `zod` installed in your project:
```bash
npm install zod
```

### The Program (`main.mjs`)

```javascript
import { z } from 'zod';

// 1. Define the signup schema
const signupSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
  age: z.number().int().min(13, "Must be at least 13 years old").optional(),
});

// 2. Parse one valid and one invalid object
const validData = {
  email: "user@example.com",
  password: "securePassword123",
  age: 25,
};

const invalidData = {
  email: "not-an-email",
  password: "short",
  age: 10,
};

console.log("--- Valid Parsing ---");
const validResult = signupSchema.safeParse(validData);
console.log("Success:", validResult.success);

console.log("\n--- Invalid Parsing ---");
const invalidResult = signupSchema.safeParse(invalidData);

if (!invalidResult.success) {
  // Print every issue's path and message
  console.log("Individual Issues:");
  invalidResult.error.issues.forEach((issue) => {
    console.log(`Path: ${issue.path.join('.')}, Message: ${issue.message}`);
  });

  // Print errors grouped per field
  console.log("\nErrors grouped by field:");
  console.log(invalidResult.error.flatten().fieldErrors);
}

// 3. Create an admin schema by extending the signup schema
const adminSchema = signupSchema.extend({
  role: z.enum(['admin', 'user']),
});

console.log("\n--- Admin Parsing ---");
const adminData = {
  email: "admin@example.com",
  password: "adminPassword123",
  age: 30,
  role: "admin",
};

const adminResult = adminSchema.safeParse(adminData);
console.log("Admin Success:", adminResult.success);
console.log("Admin Data:", adminResult.data);
```

### How to run
1. Save the code above into a file named `main.mjs`.
2. Run the command:
   ```bash
   node main.mjs
   ```

This program utilizes `zod`'s `safeParse` for validation, `flatten()` for grouping field errors, and `extend()` for schema composition, all of which are stable, non-deprecated APIs in the current version of Zod.