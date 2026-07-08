from genlayer import *

class SimpleStorage(gl.Contract):
    # Persistent storage fields statically declared at class level
    value: gl.u256
    owner: gl.Address

    def __init__(self, initial_value: gl.u256):
        # Initializing storage variables
        self.value = initial_value
        self.owner = gl.message.sender  # Stores caller's address

    @gl.public.view
    def get_value(self) -> gl.u256:
        """
        Public view function to retrieve the stored value.
        Read-only, does not modify state.
        """
        return self.value

    @gl.public.write
    def set_value(self, new_value: gl.u256):
        """
        Public write function to update the stored value.
        Only the owner can update the value.
        """
        if gl.message.sender != self.owner:
            raise Exception("Only the owner can update the value")
        
        self.value = new_value
