# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
from datetime import datetime

class OmniSLA(gl.Contract):
    # Persistent storage fields
    provider: Address
    client: Address
    target_url: str
    collateral_required: u256
    premium_required: u256
    collateral_funded: u256
    premium_funded: u256
    validation_strategy: str
    validation_rule: str
    status: str
    last_check_datetime: str
    violations_count: u256
    max_allowed_violations: u256
    sla_end_time_iso: str

    def __init__(
        self,
        provider: Address,
        client: Address,
        target_url: str,
        collateral_required: u256,
        premium_required: u256,
        validation_strategy: str,
        validation_rule: str,
        max_allowed_violations: u256,
        sla_end_time_iso: str
    ):
        self.provider = Address(provider) if isinstance(provider, (str, bytes)) else provider
        self.client = Address(client) if isinstance(client, (str, bytes)) else client
        self.target_url = target_url
        self.collateral_required = collateral_required
        self.premium_required = premium_required
        self.validation_strategy = validation_strategy
        self.validation_rule = validation_rule
        self.max_allowed_violations = max_allowed_violations
        self.sla_end_time_iso = sla_end_time_iso
        
        self.collateral_funded = u256(0)
        self.premium_funded = u256(0)
        self.status = "Created"
        self.last_check_datetime = ""
        self.violations_count = u256(0)

    @gl.public.view
    def get_status(self) -> str:
        return self.status

    @gl.public.view
    def get_details(self) -> str:
        details = {
            "provider": self.provider.as_hex,
            "client": self.client.as_hex,
            "target_url": self.target_url,
            "collateral_required": int(self.collateral_required),
            "premium_required": int(self.premium_required),
            "collateral_funded": int(self.collateral_funded),
            "premium_funded": int(self.premium_funded),
            "validation_strategy": self.validation_strategy,
            "validation_rule": self.validation_rule,
            "status": self.status,
            "last_check_datetime": self.last_check_datetime,
            "violations_count": int(self.violations_count),
            "max_allowed_violations": int(self.max_allowed_violations),
            "sla_end_time_iso": self.sla_end_time_iso
        }
        return json.dumps(details, sort_keys=True)

    @gl.public.write.payable
    def deposit_collateral(self) -> None:
        if gl.message.sender_address != self.provider:
            raise gl.vm.UserError("Only provider can deposit collateral")
        if self.status != "Created":
            raise gl.vm.UserError("SLA not in Created status")
        
        self.collateral_funded = u256(int(self.collateral_funded) + int(gl.message.value))
        self._check_and_activate()

    @gl.public.write.payable
    def deposit_premium(self) -> None:
        if gl.message.sender_address != self.client:
            raise gl.vm.UserError("Only client can deposit premium")
        if self.status != "Created":
            raise gl.vm.UserError("SLA not in Created status")
        
        self.premium_funded = u256(int(self.premium_funded) + int(gl.message.value))
        self._check_and_activate()

    def _check_and_activate(self) -> None:
        if int(self.collateral_funded) >= int(self.collateral_required) and int(self.premium_funded) >= int(self.premium_required):
            self.status = "Active"

    @gl.public.write
    def refund(self) -> None:
        if self.status != "Created":
            raise gl.vm.UserError("Cannot refund after activation")
        
        sender = gl.message.sender_address
        if sender == self.provider:
            amount = int(self.collateral_funded)
            if amount > 0:
                self.collateral_funded = u256(0)
                gl.get_contract_at(sender).emit_transfer(value=u256(amount), on="finalized")
        elif sender == self.client:
            amount = int(self.premium_funded)
            if amount > 0:
                self.premium_funded = u256(0)
                gl.get_contract_at(sender).emit_transfer(value=u256(amount), on="finalized")
        else:
            raise gl.vm.UserError("Unauthorized sender for refund")

    @gl.public.write
    def check_sla(self) -> bool:
        if self.status != "Active":
            raise gl.vm.UserError("SLA is not Active")
        
        self.last_check_datetime = gl.message_raw['datetime']
        
        # 1. Define non-deterministic block
        def execute_check() -> bool:
            # Fetch target endpoint
            response = gl.nondet.web.get(self.target_url)
            
            if self.validation_strategy == "contains":
                # Check if expected substring is present in response
                resp_str = str(response)
                return self.validation_rule in resp_str
                
            elif self.validation_strategy == "semantic":
                # Run LLM evaluation on the response content
                task = f"""
                Evaluate the following API/website response content:
                ---
                {str(response)}
                ---
                Does this content satisfy the following criteria: "{self.validation_rule}"?
                Respond with a JSON object containing a boolean field:
                {{
                    "compliant": bool
                }}
                It is mandatory that you respond only using the JSON format above, nothing else.
                Don't include any other words or characters, your output must be only JSON.
                """
                result_raw = gl.nondet.exec_prompt(task, response_format="json")
                if isinstance(result_raw, dict):
                    return bool(result_raw.get("compliant", False))
                # Fallback parser if string is returned
                try:
                    result = json.loads(str(result_raw))
                    return bool(result.get("compliant", False))
                except Exception:
                    return False
            else:
                return False

        # 2. Define validator function
        def validate_check(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            
            # Run same logic to verify
            my_res = execute_check()
            return bool(leader_result.calldata) == my_res

        # 3. Run consensus
        is_compliant = gl.vm.run_nondet_unsafe(execute_check, validate_check)
        
        if not is_compliant:
            self.violations_count = u256(int(self.violations_count) + 1)
            if int(self.violations_count) >= int(self.max_allowed_violations):
                self._slash()
                return False
        
        return is_compliant

    def _slash(self) -> None:
        self.status = "Violated"
        payout = int(self.collateral_funded) + int(self.premium_funded)
        self.collateral_funded = u256(0)
        self.premium_funded = u256(0)
        gl.get_contract_at(self.client).emit_transfer(value=u256(payout), on="finalized")

    @gl.public.write
    def close_sla(self) -> None:
        if self.status != "Active":
            raise gl.vm.UserError("SLA is not Active")
        
        current_time = datetime.fromisoformat(gl.message_raw['datetime'])
        end_time = datetime.fromisoformat(self.sla_end_time_iso)
        if current_time < end_time:
            raise gl.vm.UserError("SLA duration has not ended yet")
        
        self.status = "Closed"
        payout = int(self.collateral_funded) + int(self.premium_funded)
        self.collateral_funded = u256(0)
        self.premium_funded = u256(0)
        gl.get_contract_at(self.provider).emit_transfer(value=u256(payout), on="finalized")
