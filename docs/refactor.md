# Notes for refactor

## Changed items
- new_user -> NewUser 

## Items to look at later
- `authentication.apis.RegisterUserNoVerificationAPI` has no swagger or tests
- fix email and secrets
<<<<<<< Local Changes
- install a `test_template` for Swagger responses
- provide example values that are usable for testing APIs.
- certifying key for prefix as a JWT? 
- owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 

- need tests for token
