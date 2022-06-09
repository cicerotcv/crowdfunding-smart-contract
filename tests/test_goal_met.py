import os
import pytest
import brownie
import time


TARGET = 100

@pytest.fixture(scope="module", autouse=True)
def crowd_contract(CrowdFunding, accounts):
    # deploy the contract with the initial values as a constructor argument
    contract = CrowdFunding.deploy(TARGET, time.time() + 10, {'from': accounts[0]})
    return contract

@pytest.fixture(scope="module", autouse=True)
def expired_contract(CrowdFunding, accounts):
    contract = CrowdFunding.deploy(TARGET, int(time.time()) + 1, {"from": accounts[0]})
    contract.donate({"from": accounts[1], "value": 101})
    while time.time() < contract.deadline():
        time.sleep(1)
    return contract


def initial_state(crowd_contract, expired_contract):
    # Check if the constructor of the contract is set up properly
    assert crowd_contract.goal() == TARGET
    assert crowd_contract.deadline() == pytest.approx(time.time() + 10, abs=1)

    assert expired_contract.goal() == TARGET
    assert expired_contract.deadline() > 0 # contract deadline is not the default value (0)
    assert expired_contract.deadline() < time.time() # contract expired


class TestDonations:
    @staticmethod
    def test_donate_before_deadline(crowd_contract, accounts):
        # Donation Test
        crowd_contract.donate({'from': accounts[2], 'value': 10})
        # Directly access donations
        assert crowd_contract.donors(accounts[2].address)['donated_amount'] == 10
        
        # Donation Test Other account
        crowd_contract.donate({'from': accounts[1], 'value': 20})
        # Directly access donations
        assert crowd_contract.donors(accounts[1].address)['donated_amount'] == 20

        # contract's balance must be the sum
        assert crowd_contract.balance() == 30

    @staticmethod
    def test_donate_after_deadline(expired_contract, accounts):
        # Donate after deadline
        with brownie.reverts("Contract must be active for you to be able to donate"):
            expired_contract.donate({"from": accounts[3], 'value': 10})


class TestClaim:
    @staticmethod
    def test_claim_before_deadline(crowd_contract, accounts):
        # Claim refund before deadline 
        with brownie.reverts("Contract must have ended for the owner to be able to claim donations"):
            crowd_contract.claim_donations({"from": accounts[0]})

    @staticmethod
    def test_non_owner_claim(expired_contract, accounts):
        # Non owner trying to claim
        with brownie.reverts("You must be the contract's owner to be able to claim donations"):
            expired_contract.claim_donations({"from": accounts[1]})
    
    @staticmethod
    def test_claim_donations(expired_contract, accounts):
        # goal unmet
        expired_contract.claim_donations({"from": accounts[0]})
        assert expired_contract.balance() == 0



class TestRefund:
    @staticmethod
    def test_refund_before_deadline(crowd_contract, accounts):
        with brownie.reverts():
            crowd_contract.claim_refund({"from": accounts[1]})

        with brownie.reverts():
            crowd_contract.claim_refund({"from": accounts[2]})

    @staticmethod
    def test_refund_after_deadline(expired_contract, accounts):
        with brownie.reverts("Contract's goal must not have been met for the donors to be able to claim refund"):
            expired_contract.claim_refund({"from": accounts[1]})

    @staticmethod
    def test_non_donor_refund_before_deadline(crowd_contract, accounts):
        with brownie.reverts("Contract must have ended for the donors to be able to claim refund"):
            crowd_contract.claim_refund({"from": accounts[3]})

    @staticmethod
    def test_non_donor_refund_after_deadline(expired_contract, accounts):
        with brownie.reverts("Contract's goal must not have been met for the donors to be able to claim refund"):
            expired_contract.claim_refund({"from": accounts[3]})
