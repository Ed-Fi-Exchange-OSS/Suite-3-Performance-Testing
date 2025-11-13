### **API Design Document: Bulk Operations Endpoint**

#### **1. Overview**

**1.1. Problem Statement**
The current application architecture experiences significant PostgreSQL "WAL write waits." This is caused by chatty, single-commit-per-API-call transactions. For every `INSERT`, `UPDATE`, or `DELETE`, the application pays the full disk I/O cost (`fsync`) for a single operation, creating a performance bottleneck.

**1.2. Proposed Solution**
Implement a single, transactional "Unit of Work" endpoint. This endpoint will accept an array of operations (`create`, `update`, `delete`) to be executed within a single database transaction.

This "chunky" RPC-style (Remote Procedure Call) endpoint amortizes the `fsync` cost across many operations, drastically improving write throughput. It also guarantees atomicity, ensuring that a set of related operations (e.g., creating a `Student` and their `StudentSchoolAssociation`) either succeeds or fails together.

#### **2. Requirements**

  * **Performance:** Must significantly reduce database write-wait times by processing multiple operations in one transaction.
  * **Atomicity:** The entire batch of operations must succeed or fail as a single atomic unit. No partial data will be committed.
  * **Flexibility:** Must support `create`, `update`, and `delete` operations.
  * **Resource Agnostic:** Must handle operations for any resource type (`Student`, `School`, `Section`, etc.) in a single call.
  * **Identifier Support:** Must be able to identify documents for `update`/`delete` using either their public-facing `uuid` or their internal `naturalKey` (which may be composite).
  * **Clear Error Reporting:** If the batch fails, the API must return a specific, actionable error, pinpointing which operation failed and why.

#### **3. API Endpoint Design**

**Endpoint:** `POST /api/bulk`

**Request Body:**
A JSON array of *Operation Objects*. Operations are guaranteed to be executed in the order they appear in the array.

**Operation Object Structure:**
An object with the following properties:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `op` | string | Yes | The operation to perform: `"create"`, `"update"`, `"delete"`. |
| `resource` | string | Yes | The type of resource, e.g., `"Student"`, `"Section"`. |
| `payload` | object | For `create`/`update` | The JSON document or partial document for the operation. |
| `uuid` | string | For `update`/`delete`\* | The document's public UUID. *Must provide this OR `naturalKey`. |
| `naturalKey` | object | For `update`/`delete`* | The document's natural key(s). \*Must provide this OR `uuid`. |

-----

#### **4. Operation Definitions**

**4.1. `create` Operation**
Inserts a new document. The `payload` contains the full document. Natural keys must be present in the payload.

```json
{
  "op": "create",
  "resource": "Student",
  "payload": {
    "studentNaturalId": "S-JANE-DOE-001",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane@example.com"
  }
}
```

**4.2. `update` Operation**
Performs a partial update on an existing document. The `payload` should only contain the fields to be changed.

  * **Update by `uuid`:**
    ```json
    {
      "op": "update",
      "resource": "Student",
      "uuid": "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
      "payload": {
        "email": "jane.doe.new@example.com"
      }
    }
    ```
  * **Update by Composite `naturalKey`:**
    ```json
    {
      "op": "update",
      "resource": "Section",
      "naturalKey": {
        "sectionName": "Algebra I",
        "sectionIdentifier": "FALL2025-A1-003"
      },
      "payload": {
        "roomNumber": "204B"
      }
    }
    ```

**4.3. `delete` Operation**
Deletes an existing document.

  * **Delete by `uuid`:**
    ```json
    {
      "op": "delete",
      "resource": "Student",
      "uuid": "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
    }
    ```
  * **Delete by `naturalKey`:**
    ```json
    {
      "op": "delete",
      "resource": "Section",
      "naturalKey": {
        "sectionName": "Algebra I",
        "sectionIdentifier": "FALL2025-A1-003"
      }
    }
    ```

-----

#### **5. Server-Side Logic**

1.  The server receives the `POST /api/bulk` request.
2.  **`BEGIN TRANSACTION;`**
3.  Iterate through the operations array in order.
4.  For each operation:
      * **Authorization:** Check if the user is authorized to perform this action on this resource (e.g., can they *really* delete a `School`?).
      * **Validation:**
          * For `update`/`delete`, validate that *exactly one* of `uuid` or `naturalKey` is present.
      * **Execution:**
          * Use a `switch (op.resource)` to map to the correct service/repository.
          * Use a `switch (op.op)` to call the correct `Create()`, `Update()`, or `Delete()` method.
          * The `Update()` and `Delete()` methods will build their `WHERE` clause dynamically based on whether `uuid` or the `naturalKey` object was provided.
5.  If the loop completes without any exceptions:
      * **`COMMIT TRANSACTION;`**
      * Return a `200 OK` response.
6.  If *any* operation (authorization, validation, or execution) throws an exception:
      * **`ROLLBACK TRANSACTION;`**
      * Do *not* proceed to the next operation.
      * Return a `400 Bad Request` response.

#### **6. API Contract: Success Response (`200 OK`)**

The response will be a JSON array that mirrors the request, providing the outcome of each operation. For `create` operations, this includes the newly generated `uuid`.

**Response Body:**

```json
[
  {
    "status": "success",
    "op": "create",
    "resource": "Student",
    "uuid": "b8d9e1a0-4f3a-4c8d-8a1e-6f9b2c7d0e1f" // New ID
  },
  {
    "status": "success",
    "op": "update",
    "resource": "Section"
  },
  {
    "status": "success",
    "op": "delete",
    "resource": "Student"
  }
]
```

#### **7. API Contract: Error Response (`400 Bad Request`)**

If any operation fails, the *entire transaction* is rolled back and a single error object is returned. This object pinpoints the *first* operation that failed.

**Response Body:**

```json
{
  "error": "Batch operation failed and was rolled back.",
  "failedOperation": {
    "index": 1,
    "resource": "Student",
    "errorCode": "DUPLICATE_NATURAL_KEY",
    "message": "Operation 1 (create 'Student') failed: A student with natural key 'S-JANE-DOE-001' already exists."
  }
}
```

#### **8. Future Considerations**

  * **Batch Size Limits:** Implement a reasonable limit (e.g., 100 or 1,000 operations per batch) to prevent abuse and excessively long-running transactions.
  * **Permissions:** The authorization logic in the loop is critical. A user might be allowed to `create Student` but not `delete School`. This must be checked *per-operation*.
