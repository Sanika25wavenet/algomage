# FIXING MONGODB PASSWORD

The error `bad auth` means the **Username** or **Password** is wrong.
You likely created a **Collection**/Table named `users`, but you did NOT create a **Database User** with that name/password.

**Follow these 6 steps EXACTLY:**

1.  **Log in** to [MongoDB Atlas](https://cloud.mongodb.com).
2.  Look at the **LEFT SIDEBAR**. Under the **SECURITY** section, click on **Database Access**.
    *(Do NOT click on "Database" or "Collections")*
3.  Click the green button **+ Add New Database User**.
4.  **Fill in the form:**
    *   **Authentication Method:** Password
    *   **Username:** `admin`
    *   **Password:** `password123` (Type this exactly)
    *   **Database User Privileges:** Read and write to any database
5.  Click the green button **Add User** at the bottom.
6.  **WAIT** about 1-2 minutes for the change to deploy.

**NOW, check your code:**

Your `server/.env` file should look fully like this:

```env
MONGODB_URL=mongodb+srv://admin:password123@attendance-cluster.ifwp4fg.mongodb.net/?appName=attendance-cluster
DATABASE_NAME=event_photo_retrieval
```

*Note: If you already have a user named `admin`, EDIT it and change the password to `password123`.*
