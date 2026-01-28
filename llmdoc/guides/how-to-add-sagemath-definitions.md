# How to Add SageMath Standard Library Definitions

1. **Identify missing symbols:** Open a .sage file, type SageMath function/class name, observe if semantic highlighting is missing.

2. **Locate definition file:** Navigate to `src/server/predefinition.py`.

3. **Add function names:** For standalone functions, add to `FUNCTIONS` set (`predefinition.py:17-93`).
   - Example: Add `"my_function"` to the set
   - Functions are highlighted when called or defined via `def`

4. **Add class definitions:** For classes with methods/properties, add entry to `CLASSES` dictionary (`predefinition.py:96-192`).
   - Format: `"ClassName": {"methods": ["method1", "method2"], "properties": {"prop1": "Type1"}}`
   - Methods are highlighted when accessed via `instance.method()`
   - Properties are highlighted when accessed via `instance.prop`

5. **Restart LSP:** In VS Code, run "SageMath: Restart SageMath LSP" command or reload window.

6. **Verify changes:** Reopen .sage file and confirm new symbols are semantically highlighted.

**Note:** The `CLASSES` dictionary structure enables member resolution for `obj.member` patterns when `obj`'s type is known from prior assignment. See `utils.py:330-336` for resolution logic.

**Reference:** Consult [SageMath Documentation](https://doc.sagemath.org/html/en/reference/index.html) for complete standard library reference.
