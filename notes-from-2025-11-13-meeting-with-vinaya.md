Test in Azure?  3 separate VMs

10M records

Move to relational flattening

You need streaming

What about WAL on SQL Server


Packed binary JSON? Can't query, post-streaming de-compress


----

1. Document table only + Relational (Rewrite everything)


2. Leave as is -> 3 table + relational flattening, relational optional

  Idea - spike a simple single relational + auth dummy to simulate load of both


3. Relational plus binary




----

What is happening with read?????

What does a read design look like for relational-optional???

Read performance - create timestamp in natural order, UUIDv7 helps with that, sub partition by ResourceName???

Priority is get ALL by resource in create order


