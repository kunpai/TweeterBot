#importing all dependencies
import numpy as np
import tweepy


#variables for accessing twitter API
consumer_key='kFcQTRaJGfYoHky4qZAFJtv6k'
consumer_secret_key='LssjIqDXnmt4trErViOnMdhwnoWNEZmFF7CidKeQppE1r3zY2w'
access_token='546617527-KpG0toJkKJQaFZZoJenmZ3JhSE4U8r0sqg55kQ20'
access_token_secret='Qsmwox1vwSOB0UTRaahwSNraH2isAyt4iCfVV7BZrw6HQ'

#authenticating to access the twitter API
auth=tweepy.OAuthHandler(consumer_key,consumer_secret_key)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)

# tweet=input('enter the tweet')
# #Generate text tweet
# api.update_status(tweet)

tweet_text="@warikoo"
image_path ='ghiasi.png'
#api.update_status(tweet_text)
#Generate text tweet with media (image)
#api.update_status_with_media(tweet_text, image_path)
# #api.update_status(status)
# obj = api.search_users(q="Naval")
# user_ids = [user.screen_name for user in obj]
# print(user_ids)

api.create_friendship(user_id="1076254901565571073")