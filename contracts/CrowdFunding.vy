# @version ^0.3.2
# Crowdfunding Project v0.1.0


# Struct definitions

struct Donor:
  id: address # id
  donated_amount: uint256 # donated value

# contract owner
owner: public(address)

# contract donors
donors: public(HashMap[address, Donor])

# contract goal
goal: public(uint256)

# currently reached value
current_reached: public(uint256)

# contract deadline
deadline: public(uint256)

# contract goal status
goal_status: public(bool)


# ------------- Internal useful methods ------------- #


@internal
def contract_ended() -> bool:
  return block.timestamp > self.deadline


@internal
def caller_is_owner(_caller:address) -> bool:
  return self.owner == _caller 


@internal
def goal_is_met() -> bool:
  self.goal_status = self.goal_status or self.balance >= self.goal
  return self.goal_status

# ------------- External methods ------------- #


@external
def __init__(goal: uint256, deadline:uint256):
  assert block.timestamp < deadline, "Deadline is before current time"
  self.owner = msg.sender
  self.goal = goal
  self.goal_status = False
  self.deadline = deadline


@external
@payable
def donate():
  # guarantee the current block is before the contracts' deadline
  # (the contract must have not ended yet)
  assert not self.contract_ended(), "Contract must be active for you to be able to donate"

  # register donations
  self.donors[msg.sender].donated_amount += msg.value


@external
def claim_donations():
  # claim is only available after the deadline is met
  assert self.contract_ended(), "Contract must have ended for the owner to be able to claim donations"
  # only contract's owner is able to claim the raised donations
  assert self.caller_is_owner(msg.sender), "You must be the contract's owner to be able to claim donations"
  # claim is only available if contract's goal is met
  assert self.goal_is_met(), "Contract's goal must have been met for you to be able to claim donations"

  send(self.owner, self.balance)


@external
def claim_refund():
  # refund is only available after contracts end
  assert self.contract_ended(), "Contract must have ended for the donors to be able to claim refund"
  # refund is only available if the goal is not met
  assert not self.goal_is_met(), "Contract's goal must not have been met for the donors to be able to claim refund"
  # only donors are able to refund
  assert self.donors[msg.sender].donated_amount > 0, "Only donors are able to claim refund"

  refund_amount:uint256 = self.donors[msg.sender].donated_amount
  send(msg.sender, self.donors[msg.sender].donated_amount)
  self.donors[msg.sender].donated_amount = 0


# ------------- Readonly methods ------------- #


@view
@external
def read_balance() -> uint256:
  return self.balance
