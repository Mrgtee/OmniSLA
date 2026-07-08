# Persistent Storage Types in GenLayer

Intelligent Contracts executing within the GenVM require specific type annotations for variables that persist across blockchain state changes. Standard Python collections (like `list` and `dict`) and default integers (`int`) are NOT storage-compatible and will cause compilation/linting errors.

## Storage-Compatible Types

### 1. Sized Integer Types
GenVM supports fixed-size integer types for precise gas computation and range checking:
- **Unsigned Integers**: `gl.u8`, `gl.u16`, `gl.u32`, `gl.u64`, `gl.u128`, `gl.u256`
- **Signed Integers**: `gl.i8`, `gl.i16`, `gl.i32`, `gl.i64`, `gl.i128`, `gl.i256`
- **Arbitrary Precision**: `gl.bigint` (use this if size is unbounded, but sized integers are preferred).

### 2. Blockchain primitives
- **`gl.Address`**: Represents a 20-byte address (EVM and GenLayer account compatible).

### 3. Dynamic Array (`gl.DynArray[T]`)
Replaces Python's standard `list`.
- **Declaration**: `my_list: gl.DynArray[gl.u256]`
- **Instantiation**: Usually initialized implicitly or in `__init__`.
- **Supported Methods**:
  - `.append(value)`: Append an element.
  - `.pop()`: Remove and return the last element.
  - `len(self.my_list)`: Get length.
  - `self.my_list[index]`: Access/modify element.

### 4. Tree Map (`gl.TreeMap[K, V]`)
Replaces Python's standard `dict`.
- **Declaration**: `balances: gl.TreeMap[gl.Address, gl.u256]`
- **Supported Methods**:
  - `self.balances[key] = value`: Insert/update key-value pair.
  - `self.balances[key]`: Access value.
  - `key in self.balances`: Check membership.
  - `del self.balances[key]`: Delete entry.

---

## Important Rules & Best Practices

1. **Static Declaration**: All persistent state variables must be declared as class annotations in the main contract class body.
   ```python
   class MyContract(gl.Contract):
       balance: gl.u256  # Correct
   ```
2. **No Dynamic Persistence**: Assigning new fields to `self` dynamically (e.g. `self.temp_var = 10` inside a method without a class-level declaration) will NOT persist the data after the transaction ends.
3. **Generic Type Arguments**: Generic classes must be fully instantiated with their type arguments:
   - **Correct**: `gl.TreeMap[gl.Address, gl.u256]`
   - **Incorrect**: `gl.TreeMap`
4. **No Nested Complex Storage**: Nesting complex types inside collections (e.g., `DynArray[TreeMap[...]]` or `TreeMap[str, DynArray[...]]`) is generally not supported. Use separate mappings or structures where possible.
