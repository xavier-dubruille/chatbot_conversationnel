from fastcore.foundation import L


class ConnectedUser:
    def __init__(self, request_or_scope):
        headers = request_or_scope.headers

        default = "Anonymous"
        if hasattr(headers, "get"):
            self.user_name = headers.get("X-Remote-User", default)
        elif isinstance(headers, (list, tuple, L)):
            self.user_name = next(
                (value.decode() for key, value in headers if key.decode().lower() == "x-remote-user"), default)
        else:
            self.user_name = default

        if self.user_name == default:
            print("Connected user not identified !")

    @property
    def user_type(self):
        if self.user_name.startswith("TI"):
            return 'ti'
        elif self.user_name.startswith("eB"):
            return 'eb'
        else:
            return 'other'

    @property
    def is_student(self):
        return self.user_type != 'other'

    def can_see_scenario(self, scenario_name):
        user_type = self.user_type
        if user_type == 'ti':
            return "TI" in scenario_name
        elif user_type == 'eb':
            return "eB" in scenario_name
        else:
            return True
