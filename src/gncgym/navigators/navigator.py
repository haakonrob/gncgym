class Navigator:
    def navigate(self):
        raise NotImplementedError("The navigate function has not been implemented.")


class IdentityNavigator:
    def navigate(self, state):
        return state
