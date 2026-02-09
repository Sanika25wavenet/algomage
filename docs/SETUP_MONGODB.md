# How to Get Your MongoDB Atlas Connection String

Since you are using MongoDB Atlas, follow these steps to get your connection string:

1. **Log in to MongoDB Atlas**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and log in.

2. **Locate Your Cluster**
   - On the main dashboard, find your Cluster (e.g., "Cluster0").
   - Click the **Connect** button.

3. **Set Up Connection Security (If not done already)**
   - **Add your IP Address**: Click "Add your current IP Address" or choose "Allow Access from Anywhere" (0.0.0.0/0) for development.
   - **Create a Database User**:
     - Enter a **Username** (e.g., `admin`).
     - Enter a **Password** (make it strong but memorable).
     - Click **Create Database User**.

4. **Choose a Connection Method**
   - Choose **Drivers**.
   - Select **Driver**: `Python`.
   - Select **Version**: `3.6 or later`.

5. **Copy the Connection String**
   - You will see a string like:
     ```
     mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
     ```
   - Copy this string.

6. **Update Your Project**
   - Open `server/.env`.
   - Paste the string into `MONGODB_URL=`.
   - **IMPORTANT**: Replace `<password>` with your actual password.
     - Example: If password is `supersecret`, replace `<password>` with `supersecret` (remove `<` and `>`).

7. **Save the File**
