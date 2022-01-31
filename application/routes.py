import uuid

import requests
from flask import current_app as app, request, jsonify
from flask import redirect, url_for
from flask_dance.contrib.twitter import twitter

from .models import User, db


@app.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")

    if resp.ok:
        twitter_username = resp.json()["screen_name"]
        user_sess = uuid.uuid4().__str__()
        new_user = User(username=twitter_username, id=user_sess)
        x = db.session.query(User).get(twitter_username)
        if not x:
            db.session.add(new_user)
            db.session.commit()
        return redirect("https://www.psychokitties.io/stream")
    else:
        print("Ain't logged in")
        # Redirect to login again


@app.route("/verify-crypto")
def verify():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    args = request.args
    crypto_username = args.get('username')
    discord = args.get('discord')
    if not crypto_username or len(crypto_username) == 0:
        return jsonify({"error": "Crypto Username not set", }), 403
    if not discord or len(discord) == 0:
        return jsonify({"error": "Discord Username not set", }), 403
    twitter_username = resp.json()["screen_name"]
    try:
        url = "https://crypto.com/nft-api/graphql"
        username = crypto_username
        payload = "{\r\n\t\"operationName\": \"User\",\r\n\t\"variables\": {\r\n\t\t\"id\": \"" + username + "\",\r\n\t\t\"cacheId\": \"getUserQuery-Profile-" + username + "\"\r\n\t},\r\n\t\"query\": \"query User($id: ID!, $cacheId: ID) {   public(cacheId: $cacheId) {     user(id: $id) {       uuid       verified       id       username       bio       displayName       instagramUsername       facebookUsername       twitterUsername       isCreator       canCreateAsset       croWalletAddress       avatar {         url         __typename       }       cover {         url         __typename       }       __typename     }     __typename   } } \"\r\n}"
        headers = {
            'content-type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        registered_username = response.json()['data']['public']['user']['twitterUsername']
        # BYPASS 1
        # if str(registered_username).lower() == str("ugonzo_art").lower():
        if str(registered_username).lower() == str(twitter_username).lower():
            x = db.session.query(User).get(twitter_username)
            x.cryptoUsername = crypto_username
            x.discordUsername = discord
            x.isTwitterMatching = True
            db.session.commit()
            return jsonify({"success": "Crypto.org and twitter are matching", }), 200
        else:
            return jsonify({"error": "Twitter on Crypto.org not matching", }), 401
    except:
        return jsonify({"error": "Couldn't fetch data from Crypto.org", }), 400


@app.route("/verify-holder")
def verify_holder():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    twitter_username = resp.json()["screen_name"]
    x = db.session.query(User).get(twitter_username)
    if not x.isTwitterMatching:
        return jsonify({"error": "Twitter on Crypto.org not matching", }), 401
    try:
        un = x.cryptoUsername
        # BYPASS 2
        # un="mrumantha"
        url = "https://crypto.com/nft-api/graphql"

        payload = "{\n    \"operationName\": \"GetAssets\",\n    \"variables\": {\n        \"ownerId\": \"" + un + "\",\n        \"first\": 6000,\n        \"skip\": 0,\n        \"cacheId\": \"getAssetsQuery-ProfileCollectibleTab-ugonzo_art\",\n        \"collectionId\": \"faa3d8da88f9ee2f25267e895db71471\"\n    },\n    \"query\": \"fragment UserData on User {\\n  uuid\\n  id\\n  username\\n  displayName\\n  isCreator\\n  avatar {\\n    url\\n    __typename\\n  }\\n  __typename\\n}\\n\\nquery GetAssets($audience: Audience, $brandId: ID, $categories: [ID!], $collectionId: ID, $creatorId: ID, $ownerId: ID, $first: Int!, $skip: Int!, $cacheId: ID, $hasSecondaryListing: Boolean, $where: AssetsSearch, $sort: [SingleFieldSort!], $isCurated: Boolean, $createdPublicView: Boolean) {\\n  public(cacheId: $cacheId) {\\n    assets(\\n      audience: $audience\\n      brandId: $brandId\\n      categories: $categories\\n      collectionId: $collectionId\\n      creatorId: $creatorId\\n      ownerId: $ownerId\\n      first: $first\\n      skip: $skip\\n      hasSecondaryListing: $hasSecondaryListing\\n      where: $where\\n      sort: $sort\\n      isCurated: $isCurated\\n      createdPublicView: $createdPublicView\\n    ) {\\n      id\\n      name\\n      copies\\n      copiesInCirculation\\n      creator {\\n        ...UserData\\n        __typename\\n      }\\n      main {\\n        url\\n        __typename\\n      }\\n      cover {\\n        url\\n        __typename\\n      }\\n      royaltiesRateDecimal\\n      primaryListingsCount\\n      secondaryListingsCount\\n      primarySalesCount\\n      totalSalesDecimal\\n      defaultListing {\\n        editionId\\n        priceDecimal\\n        mode\\n        auctionHasBids\\n        __typename\\n      }\\n      defaultAuctionListing {\\n        editionId\\n        priceDecimal\\n        auctionMinPriceDecimal\\n        auctionCloseAt\\n        mode\\n        auctionHasBids\\n        __typename\\n      }\\n      defaultSaleListing {\\n        editionId\\n        priceDecimal\\n        mode\\n        __typename\\n      }\\n      defaultPrimaryListing {\\n        editionId\\n        priceDecimal\\n        mode\\n        auctionHasBids\\n        primary\\n        __typename\\n      }\\n      defaultSecondaryListing {\\n        editionId\\n        priceDecimal\\n        mode\\n        auctionHasBids\\n        __typename\\n      }\\n      defaultSecondaryAuctionListing {\\n        editionId\\n        priceDecimal\\n        auctionMinPriceDecimal\\n        auctionCloseAt\\n        mode\\n        auctionHasBids\\n        __typename\\n      }\\n      defaultSecondarySaleListing {\\n        editionId\\n        priceDecimal\\n        mode\\n        __typename\\n      }\\n      likes\\n      views\\n      isCurated\\n      defaultEditionId\\n      isLiked\\n      defaultOwnerEdition {\\n        id\\n        listing {\\n          priceDecimal\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\"\n}"
        headers = {
            'content-type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        assets = response.json()['data']['public']['assets']
        if len(assets) > 0:
            x.isHolder = True
            db.session.commit()
            return jsonify({"success": "User is Holding PsychoKitties NFT", }), 200
        else:
            x.isHolder = False
            db.session.commit()
            return jsonify({"error": "User isn't Holding PsychoKitties NFT", }), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Couldn't verify, please try again", }), 501


@app.route("/status")
def status():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    twitter_username = resp.json()["screen_name"]
    x = db.session.query(User).get(twitter_username)
    return jsonify(x), 200
