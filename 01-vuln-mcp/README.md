# MCP Security Lab

A deliberately vulnerable local application for learning security in
MCP-based applications.

## Planned components

- Documents server: search and read fictional documents.
- CRM server: retrieve synthetic customer records and update account notes.
- Messaging server: record simulated outgoing messages.
- Host application: connect to the servers and coordinate workflows.

Development begins with direct MCP calls. Local model integration comes later.

## Lab boundaries

Use only synthetic records, harmless canaries, and disposable fixtures.
Messages are recorded locally rather than delivered.

Local processes are not an operating-system sandbox. Intentionally vulnerable
code must not be pointed at real secrets, personal files, or production systems.

## Environment

This project uses the repository's root virtual environment.
Its Python package is named `mcp_security_lab`.

Dependency installation and usage instructions will be added as the
corresponding components are implemented.

## First direct MCP workflow

From `01-vuln-mcp/`, using the repository's shared virtual environment:

```bash
../.venv/bin/python -m mcp_security_lab.direct_client
```

The client launches the Documents server over stdio, discovers its tools,
and retrieves a fixed fictional welcome document. No model is involved.

## Document fixtures

The welcome tool reads `fixtures/documents/welcome.txt` as UTF-8 text.
Its path is resolved relative to the server source location.

The tool currently accepts no filename or path from the caller.
Fixtures contain fictional training data only.

## Automated checks

From `01-vuln-mcp/`, run:

```bash
../.venv/bin/python -m pytest -q tests
```

The welcome-document integration test launches a real stdio MCP server,
checks tool discovery, and checks the returned document text.
It requires no model or external service.

## CRM baseline

The CRM server exposes `get_customer(customer_id)` using one fictional
public training record held in memory. Persistence and authorization
exercises have not been added yet.

From `01-vuln-mcp/`, run:

```bash
../.venv/bin/python -m mcp_security_lab.crm_client
```

The CRM integration test checks an existing customer lookup and rejection
of an unknown customer ID. These checks verify normal lookup behavior,
not caller authorization.

## Inspect MCP tool definitions

From `01-vuln-mcp/`:

```bash
mkdir -p review
../.venv/bin/python -m mcp_security_lab.inspect_tools > review/discovered_tools.json
```

This launches the two configured lab servers and lists their tools.
It does not call those tools.

The snapshot records server configuration and advertised tool definitions.
It is discovery evidence, not an approval or proof of server identity.