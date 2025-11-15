### **API Design Document: Bulk Operations Endpoint**

#### **1. Overview**

**1.1. Problem Statement**
The current application architecture experiences significant PostgreSQL "WAL write waits." This is caused by chatty, single-commit-per-API-call transactions. For every `INSERT`, `UPDATE`, or `DELETE`, the application pays the full disk I/O cost (`fsync`) for a single operation, creating a performance bottleneck.

**1.2. Proposed Solution**
Implement a single, transactional "Unit of Work" endpoint. This endpoint will accept an array of operations (`create`, `update`, `delete`) to be executed within a single database transaction.

This "chunky" RPC-style (Remote Procedure Call) endpoint amortizes the `fsync` cost across many operations, drastically improving write throughput. It also guarantees atomicity, simplifies `update` logic by requiring full document replacement, and ensures that a set of related operations (e.g., creating a `Student` and their `StudentSchoolAssociation`) either succeeds or fails together.

#### **2. Requirements**

  * **Performance:** Must significantly reduce database write-wait times by processing multiple operations in one transaction.
  * **Atomicity:** The entire batch of operations must succeed or fail as a single atomic unit. No partial data will be committed.
  * **Simplicity:** `update` operations will be full replacements (`PUT` semantics) to avoid partial-update ambiguity.
  * **Flexibility:** Must support `create`, `update`, and `delete` operations.
  * **Resource Agnostic:** Must handle operations for any resource type (`Student`, `School`, `Section`, etc.) in a single call.
  * **Identifier Support:** Must be able to identify documents for `update`/`delete` using either their public-facing `uuid` or their internal `naturalKey` (which may be composite).
  * **Clear Error Reporting:** If the batch fails, the API must return a specific, actionable error, pinpointing which operation failed and why.
  * **Stability:** The server must be protected from excessively large batches.

#### **3. API Endpoint Design**

**Endpoint:** `POST /api/bulk`

**Request Body:**
A JSON array of *Operation Objects*. Operations are guaranteed to be executed in the order they appear in the array. The array **must not** contain more operations than the defined `MAX_BATCH_SIZE`.

**Operation Object Structure:**
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `op` | string | Yes | The operation to perform: `"create"`, `"update"`, `"delete"`. |
| `resource` | string | Yes | The type of resource, e.g., `"Student"`, `"Section"`. |
| `payload` | object | For `create`/`update` | The **full JSON document** for the create or update operation. |
| `uuid` | string | For `update`/`delete`\* | The document's public UUID. *Must provide this OR `naturalKey`. |
| `naturalKey` | object | For `update`/`delete`* | The document's natural key(s). \*Must provide this OR `uuid`. |

-----

#### **4. Operation Definitions**

**4.1. `create` Operation**
Inserts a new document. The `payload` contains the full document.

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
Performs a **full replacement** on an existing document. The `payload` **must** contain the *entire* document, not just the changed fields. This mirrors `PUT` semantics.

  * **Update by `uuid`:**
    ```json
    {
      "op": "update",
      "resource": "Student",
      "uuid": "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6",
      "payload": {
        "studentNaturalId": "S-JANE-DOE-001",
        "firstName": "Jane",
        "lastName": "Doe-Smith",
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
        "sectionName": "Algebra I",
        "sectionIdentifier": "FALL2025-A1-003",
        "roomNumber": "204B",
        "teacherId": 42
      }
    }
    ```

**4.3. `delete` Operation**
Deletes an existing document. No `payload` is required.

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
2.  **Batch Size Check:** Validate `request.Operations.Count <= MAX_BATCH_SIZE`. If it exceeds the limit, immediately return a `413 Payload Too Large` error.
3.  **`BEGIN TRANSACTION;`**
4.  Iterate through the operations array in order.
5.  For each operation:
      * **Authorization:** Check if the user is authorized to perform this action on this resource (e.g., can they *really* delete a `School`?).
      * **Validation:**
          * For `update`/`delete`, validate that *exactly one* of `uuid` or `naturalKey` is present.
          * For `create`/`update`, validate the `payload` against the domain model.
      * **Execution:**
          * Use a `switch (op.resource)` to map to the correct service/repository.
          * Use a `switch (op.op)`:
              * `"create"`: Call `_service.Create(op.Payload)`
              * `"update"`: Call `_service.Replace(identifier, op.Payload)`
              * `"delete"`: Call `_service.Delete(identifier)`
6.  If the loop completes without any exceptions:
      * **`COMMIT TRANSACTION;`**
      * Return a `200 OK` response.
7.  If *any* operation (batch size check, authorization, validation, or execution) throws an exception:
      * **`ROLLBACK TRANSACTION;`**
      * Do *not* proceed to the next operation.
      * Return the appropriate error response (e.g., `400 Bad Request`, `403 Forbidden`).

-----

#### **6. API Contract: Success Response (`200 OK`)**

The response will be a JSON array that mirrors the request, providing the outcome of each operation. For `create` operations, this includes the newly generated `uuid`.

**Response Body:**

```json
[
  {
    "status": "success",
    "op": "create",
    "resource": "Student",
    "uuid": "b8d9e1a0-4f3a-4c8d-8a1e-6f9b2c7d0e1f"
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

-----

#### **7. API Contract: Error Responses**

**7.1. Batch Too Large (`413 Payload Too Large`)**
Returned if the number of operations in the array exceeds `MAX_BATCH_SIZE`. The transaction is never started.

**Response Body:**

```json
{
  "error": "Batch size limit exceeded.",
  "message": "The number of operations (150) exceeds the maximum allowed (100). Please split the request into smaller batches."
}
```

**7.2. Transaction Failed (`400 Bad Request`)**
Returned if *any* operation fails during the transaction. The *entire transaction* is rolled back.

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

-----

#### **8. Operational Limits**

  * **`MAX_BATCH_SIZE`:** `500` operations.
      * This limit is a balance between performance (larger is better for throughput) and server stability (smaller prevents long-running transactions, lock contention, and high memory use).
      * A batch of 500 `INSERT`s is trivial, but a batch of 500 complex `DELETE`s with cascading referential integrity could be very expensive. This number should be tuned based on real-world performance monitoring.

#### **9. Future Considerations**

  * **Permissions:** The authorization logic in the loop is critical. A user might be allowed to `create Student` but not `delete School`. This must be checked *per-operation*.
  * **Tuning:** The `MAX_BATCH_SIZE` should be actively monitored and tuned.
