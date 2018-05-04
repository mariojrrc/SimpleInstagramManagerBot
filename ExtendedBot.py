import instabot


class ExtendedBot(instabot.Bot):
    def login(self, **args):
        if self.proxy:
            args['proxy'] = self.proxy
        if self.api.login(**args) is False:
            return False
        self.prepare()
        return True
