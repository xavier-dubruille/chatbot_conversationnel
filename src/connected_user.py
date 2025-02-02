class ConnectedUser:
    def __init__(self, request_or_scope):
        headers = request_or_scope.headers

        # if it was a 'request'
        self.user_name = headers.get("X-Remote-User", "Anonymous")

        # todo: else

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
