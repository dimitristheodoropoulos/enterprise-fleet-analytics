# MongoDB Atlas Connection for Translation Pipeline

This directory contains the MongoDB Atlas integration used by the translation pipeline.

The integration demonstrates how a document-oriented NoSQL database can be used alongside the relational PostgreSQL/Supabase components of the broader analytics platform.

---

## 🗄️ Why MongoDB?

MongoDB is used as a document-oriented storage layer for raw or semi-structured translation-related data, such as JSON responses returned by external machine-translation services.

This provides an example of a hybrid data architecture:

```text
External Translation API
          │
          ▼
     JSON Response
          │
          ▼
       MongoDB
      (NoSQL)
          │
          ▼
   Transformation /
   Processing Layer
          │
          ▼
 PostgreSQL / Supabase
       (SQL)
```

The integration demonstrates experience working with both:

* **NoSQL/document databases** for flexible JSON-oriented data.
* **Relational databases** for structured analytical storage.

MongoDB Atlas provides the managed database infrastructure, while the application connects to it using the official Python `pymongo` driver.

---

# 📁 Files

| File              | Purpose                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| `.env`            | Local environment configuration containing the MongoDB connection string. **Not committed to Git.** |
| `mongo_client.py` | Minimal MongoDB connection test / client example.                                                   |
| `README.md`       | Documentation for the MongoDB integration.                                                          |

---

# 🔐 Configuration

The MongoDB connection string is supplied through an environment variable:

```text
MONGO_URI
```

Example local `.env` file:

```dotenv
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>/<database>?retryWrites=true&w=majority
```

Replace the placeholders with the credentials and connection details provided by your MongoDB Atlas cluster.

**Never commit the actual connection string, username, password, API key, or other credentials to Git.**

---

# 🛡️ Security

The `.env` file should be excluded from version control.

The repository `.gitignore` should contain:

```gitignore
mongodb/.env
```

If the file has not yet been added to `.gitignore`, add the entry from the project root:

```bash
cd ~/Desktop/enterprise-fleet-analytics
echo "mongodb/.env" >> .gitignore
```

Then verify that Git does not track the file:

```bash
git status
```

If `.env` was previously committed, adding it to `.gitignore` is **not sufficient** to remove it from Git history. In that case, the credential should be rotated/revoked and the file should be removed from the repository history using an appropriate Git-history cleanup procedure.

---

# 🚀 Installation

Install the required Python packages:

```bash
pip install pymongo python-dotenv
```

---

# ▶️ Connection Test

Run the MongoDB client test:

```bash
python3 mongo_client.py
```

The script should load `MONGO_URI` from the local environment and attempt to establish a connection to the configured MongoDB Atlas cluster.

A successful connection confirms that:

* The MongoDB URI is available.
* The Python MongoDB driver is installed.
* The cluster is reachable.
* The supplied credentials are accepted.
* The client can communicate with MongoDB Atlas.

---

# 🧩 Role in the Broader Platform

The MongoDB integration is an example of using different database technologies for different data characteristics.

The broader platform primarily uses relational storage for structured analytical workloads, while MongoDB is suitable for retaining flexible JSON-oriented records where a rigid relational schema may not be necessary at ingestion time.

Conceptually:

```text
                         Enterprise Analytics Platform
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                     │
                   ▼                                     ▼
          Structured Operational Data            Semi-structured Data
                   │                                     │
                   ▼                                     ▼
             PostgreSQL /                         MongoDB Atlas
              Supabase                              (NoSQL)
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │
                                      ▼
                              Analytics / AI Layer
```

This separation allows raw or semi-structured external data to be handled independently from downstream analytical models and relational reporting structures.

---

# ⚠️ Notes

The MongoDB integration is primarily intended to demonstrate **NoSQL integration and document-oriented data handling** within the broader translation/data pipeline architecture.

It should not be interpreted as requiring MongoDB for every component of the platform. Relational PostgreSQL/Supabase remains appropriate for structured analytical workloads where SQL querying, relational integrity, and aggregation are central requirements.

---

# 🔒 Credential Hygiene Checklist

Before committing changes to the repository, verify:

```bash
git status
```

and confirm that the local credentials file is not listed as a tracked or staged file.

You can also check:

```bash
git ls-files mongodb/.env
```

If this command returns nothing, the file is not currently tracked by Git.

For additional protection, never place credentials directly inside Python source files or README examples.

Use environment variables or a dedicated secrets-management mechanism instead.
