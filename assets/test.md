# This is a test file

```{.mermaid loc=inline}
graph LR
 A[frontend] --> B[service proxy]
 B -->C[uSvc1]
 B-->D[uSvc2]
 D --> E((db))
 C --> E((db))
```

This should get converted
