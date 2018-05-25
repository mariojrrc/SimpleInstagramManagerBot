from tqdm import tqdm
import instabot

# Extended class to prevent command line prompting to ask credentials
class ExtendedBot(instabot.Bot):
    def login(self, **args):
        if self.proxy:
            args['proxy'] = self.proxy
        if self.api.login(**args) is False:
            return False
        self.prepare()
        return True

    def like_media_likers(self, media, nlikes=3):
        for user in tqdm(self.get_media_likers(media), desc="Media likers"):
            self.like_user(user, nlikes)
        return True

    def like_your_feed_likers(self, nlikes=3):
        last_media = self.get_your_medias()[0]
        return self.like_media_likers(last_media, nlikes=nlikes)

