from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

'''
Validates the response for a single pet matches the expected schema defined in schemas.py.

Bug found: schemas.py originally defined "name" as type "integer", but the API returns
"name" as a string (e.g. "ranger"). Fixed by changing it to "type": "string".
'''
def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 200

    # Validate the response schema against the defined schema in schemas.py
    validate(instance=response.json(), schema=schemas.pet)


'''
Extended to cover all three pet statuses. For each status, confirms:
1) the request succeeds (200)
2) every pet returned actually has the requested status
3) every pet returned matches the pet schema
'''
@pytest.mark.parametrize("status", ["available", "sold", "pending"])
def test_find_by_status_200(status):
    test_endpoint = "/pets/findByStatus"
    params = {
        "status": status
    }

    response = api_helpers.get_api_data(test_endpoint, params)

    assert response.status_code == 200

    pets = response.json()
    for pet in pets:
        assert_that(pet["status"], is_(status))
        validate(instance=pet, schema=schemas.pet)


'''
Validates that requesting a pet ID that does not exist returns a 404.
Parametrized over a few edge cases:
- a large ID that clearly doesn't exist
- 0, which is a valid int but not one of the seeded pets
- a negative ID (Flask's <int:> converter won't even match this, so this
  exercises the routing-level 404 rather than the app's explicit api.abort(404, ...))
'''
@pytest.mark.parametrize("pet_id", [999, 3, -1])
def test_get_by_id_404(pet_id):
    test_endpoint = f"/pets/{pet_id}"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 404
