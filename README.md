## Twitter Image Downloader
Download images tweeted and/or retweeted by user (who would've thought).  
Wrote this so I could download all the weeb art stuff I retweet.

![Example](https://i.imgur.com/oWiN4LV.png)

## Requirements
- Install the requirements found in requirements.txt by running `pip install -r requirements.txt`  
- Create a [Twitter App](https://developer.twitter.com/en/apps) and copy the app's credentials
- Create a `credentials.ini` file with the following format:

```ini
[CREDENTIALS]
PublicConsumerKey=public_consumer_key
SecretConsumerKey=secret_consumer_key
PublicAccessToken=public_access_token
SecretAccessToken=secret_access_token
```

## Usage
Pretty straight forward. Download the source code and run:
```bash
$ py downloader.py -u username -i number_of_tweets
```
Files will then be saved as `TweetAuthorUsername_ImageFilename.jpg`  
Note that Twitter's API limits the `number_of_tweets` to 3200.