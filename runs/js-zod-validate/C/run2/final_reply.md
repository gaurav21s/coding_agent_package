To run this program, ensure you have `zod` installed in your project: `npm install zod`.

This program uses `z.email()` (the top-level API), `z.extend()` for schema composition, and `z.treeifyError()` as the modern replacement for `.flatten()` and `.format()`.

```javascript
import { z } from 'zod';

// 1. Define Signup Schema
// Using top-level z.email() as per Zod 4 migration guide
const signupSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
  age: z.number().int().min(13).optional(),
});

// 2. Parse valid object
const validData = {
  email: "test@example.com",
  password: "password123",
  age: 25
};

console.log("--- Valid Signup ---");
const validResult = signupSchema.safeParse(validData);
console.log("Success:", validResult.success);

// 3. Parse invalid object
const invalidData = {
  email: "not-an-email",
  password: "short",
  age: 10
};

console.log("\n--- Invalid Signup ---");
const invalidResult = signupSchema.safeParse(invalidData);

if (!invalidResult.success) {
  // Print every issue's path and message
  console.log("Individual Issues:");
  invalidResult.error.issues.forEach((issue) => {
    console.log(`Path: ${issue.path.join('.')}, Message: ${issue.message}`);
  });

  // Print errors grouped per field using z.treeifyError
  console.log("\nGrouped Errors (Treeified):");
  console.log(JSON.stringify(z.treeifyError(invalidResult.error), null, 2));
}

// 4. Admin Schema
// Using .extend() as .merge() is deprecated
const adminSchema = signupSchema.extend({
  role: z.enum(['admin', 'user'])
});

const adminData = {
  email: "admin@example.com",
  password: "securepassword",
  age: 30,
  role: "admin"
};

console.log("\n--- Admin Signup ---");
const adminResult = adminSchema.safeParse(adminData);
console.log("Admin Success:", adminResult.success);
if (adminResult.success) {
  console.log("Admin Data:", adminResult.data);
}
```