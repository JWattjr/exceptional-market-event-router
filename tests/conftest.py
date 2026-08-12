"""Windows compatibility for the current genlayer-test direct loader.

The upstream direct loader uses ``mkstemp`` and unlinks the file immediately
after dup2-ing it onto stdin. Windows refuses to unlink an open file. A pipe
provides the same byte stream without a filesystem handle and keeps this
workaround isolated to the test harness.
"""

import os


if os.name == "nt":
    import gltest.direct.loader as _loader
    import gltest.direct.vm as _vm

    def _inject_message_to_fd0_windows(vm) -> None:
        # SDK paths are installed by ``load_contract_class`` immediately
        # before this hook is called, so import the SDK lazily here.
        from genlayer.py import calldata
        from genlayer.py.types import Address

        sender_addr = vm.sender
        if isinstance(sender_addr, bytes):
            sender_addr = Address(sender_addr)

        contract_addr = vm._contract_address
        if isinstance(contract_addr, bytes):
            contract_addr = Address(contract_addr)

        origin_addr = vm.origin
        if isinstance(origin_addr, bytes):
            origin_addr = Address(origin_addr)

        message_data = {
            "contract_address": contract_addr,
            "sender_address": sender_addr,
            "origin_address": origin_addr,
            "stack": [],
            "value": vm._value,
            "datetime": vm._datetime,
            "is_init": False,
            "chain_id": vm._chain_id,
            "entry_kind": 0,
            "entry_data": b"",
            "entry_stage_data": None,
        }
        encoded = calldata.encode(message_data)

        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, encoded)
        finally:
            os.close(write_fd)

        vm._original_stdin_fd = os.dup(0)
        os.dup2(read_fd, 0)
        os.close(read_fd)

    _loader._inject_message_to_fd0 = _inject_message_to_fd0_windows

    # genlayer-test currently refreshes sender/origin on warp but leaves the
    # SDK's cached message datetime unchanged. Contracts correctly read the
    # block timestamp from gl.message_raw, so keep that cache in sync here.
    _original_warp = _vm.VMContext.warp

    def _warp_windows(self, timestamp: str) -> None:
        _original_warp(self, timestamp)
        gl_module = __import__("sys").modules.get("genlayer.gl")
        if gl_module is not None and getattr(gl_module, "message_raw", None) is not None:
            gl_module.message_raw["datetime"] = timestamp

    _vm.VMContext.warp = _warp_windows
