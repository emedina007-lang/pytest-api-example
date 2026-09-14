from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

'''
Fixture: places a fresh order against whichever pet is currently 'available',
rather than hardcoding a pet_id. This keeps the test independent of run order
and of any other test mutating pet state. Returns the new order_id and the
pet_id it was placed against, so the test can verify both sides afterward.
'''
@pytest.fixture
def new_order():
    available_response = api_helpers.get_api_data("/pets/findByStatus", {"status": "available"})
    available_pets = available_response.json()
    assert len(available_pets) > 0, "No available pets to place a test order against"

    pet_id = available_pets[0]["id"]

    order_response = api_helpers.post_api_data("/store/order", {"pet_id": pet_id})
    assert order_response.status_code == 201

    order = order_response.json()
    return {"order_id": order["id"], "pet_id": pet_id}


'''
Tests the PATCH /store/order/{order_id} endpoint.
1) Uses the new_order fixture to create a fresh order against an available pet
2) PATCHes that order to a new status ("sold")
3) Validates the response code and the success message
4) Confirms the underlying pet's status was actually updated to match
'''
def test_patch_order_by_id(new_order):
    order_id = new_order["order_id"]
    pet_id = new_order["pet_id"]

    response = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "sold"})

    assert response.status_code == 200
    assert_that(response.json()["message"], is_("Order and pet status updated successfully"))

    pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert pet_response.status_code == 200
    assert_that(pet_response.json()["status"], is_("sold"))


'''
Optional edge case: PATCHing with a status outside the allowed enum should be
rejected with a 400 and a message naming the valid statuses, without updating
the order or pet.
'''
def test_patch_order_invalid_status(new_order):
    order_id = new_order["order_id"]
    pet_id = new_order["pet_id"]

    response = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "bogus"})

    assert response.status_code == 400
    assert_that(response.json()["message"], contains_string("Invalid status"))

    # Note: placing the order itself already flips the pet to 'pending'
    # (see place_order in app.py), so that's the pre-PATCH state to compare against.
    # The rejected PATCH should not move it any further (e.g. to 'sold').
    pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert_that(pet_response.json()["status"], is_("pending"))


'''
Optional edge case: PATCHing an order_id that doesn't exist should 404.
'''
def test_patch_order_not_found():
    response = api_helpers.patch_api_data("/store/order/does-not-exist", {"status": "sold"})

    assert response.status_code == 404
