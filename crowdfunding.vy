# @version ^0.2.0
# Crowdfunding Project v0.0.1


# Struct definitions

struct Donor:
  id: address # id
  donated_amount: uint256 # donated value

# contract owner
owner: address

# contract donors
donors: public(HashMap[address, Donor])

# contract goal
goal: uint256

# currently reached value
current_reached: uint256

# contract deadline
deadline: uint256


@external
def __init__(_goal: uint256, _deadline:uint256):
  assert block.timestamp < _deadline
  self.owner = msg.sender
  self.goal = _goal
  self.deadline = _deadline
  self.current_reached = 0

@external
@payable
def donate(amount:uint256):
  # guarantee the current block is before the contracts' deadline
  assert block.timestamp < self.deadline

  # register donations
  self.donors[msg.sender] = Donor({
    id: msg.sender,
    donated_amount: msg.value
  })

@external
def claim_donations():
  assert msg.sender == self.owner