from flask import Flask,redirect,render_template
import requests
from flask_oauthlib.client import OAuth
import ds_config
app = Flask(__name__)


base_uri_suffix = "/restapi"
oauth = OAuth(app)
request_token_params = {"scope": "signature",
                        "state": lambda: uuid.uuid4().hex.upper()}
if not ds_config.DS_CONFIG["allow_silent_authentication"]:
    request_token_params["prompt"] = "login"
docusign = oauth.remote_app(
    "docusign",
    consumer_key=ds_config.DS_CONFIG["ds_client_id"],
    consumer_secret=ds_config.DS_CONFIG["ds_client_secret"],
    access_token_url=ds_config.DS_CONFIG["authorization_server"] + "/oauth/token",
    authorize_url=ds_config.DS_CONFIG["authorization_server"] + "/oauth/auth",
    request_token_params=request_token_params,
    base_url=None,
    request_token_url=None,
    access_token_method="POST"
)

@app.route("/ds/callback")
def ds_callback():
    """Called via a redirect from DocuSign authentication service """
    # Save the redirect eg if present
    redirect_url = session.pop("eg", None)
    # reset the session
    ds_logout_internal()

    resp = docusign.authorized_response()
    if resp is None or resp.get("access_token") is None:
        return "Access denied: reason=%s error=%s resp=%s" % (
            request.args["error"],
            request.args["error_description"],
            resp
        )
    # app.logger.info("Authenticated with DocuSign.")
    flash("You have authenticated with DocuSign.")
    session["ds_access_token"] = resp["access_token"]
    session["ds_refresh_token"] = resp["refresh_token"]
    session["ds_expiration"] = datetime.utcnow() + timedelta(seconds=resp["expires_in"])

    # Determine user, account_id, base_url by calling OAuth::getUserInfo
    # See https://developers.docusign.com/esign-rest-api/guides/authentication/user-info-endpoints
    url = ds_config.DS_CONFIG["authorization_server"] + "/oauth/userinfo"
    auth = {"Authorization": "Bearer " + session["ds_access_token"]}
    response = requests.get(url, headers=auth).json()
    session["ds_user_name"] = response["name"]
    session["ds_user_email"] = response["email"]
    accounts = response["accounts"]
    account = None # the account we want to use
    # Find the account...
    target_account_id = ds_config.DS_CONFIG["target_account_id"]
    if target_account_id:
        account = next( (a for a in accounts if a["account_id"] == target_account_id), None)
        if not account:
            # Panic! The user does not have the targeted account. They should not log in!
            raise Exception("No access to target account")
    else: # get the default account
        account = next((a for a in accounts if a["is_default"]), None)
        if not account:
            # Panic! Every user should always have a default account
            raise Exception("No default account")

    # Save the account information
    session["ds_account_id"] = account["account_id"]
    session["ds_account_name"] = account["account_name"]
    session["ds_base_path"] = account["base_uri"] + base_uri_suffix

    if not redirect_url:
        redirect_url = url_for("index")
    return redirect(redirect_url)

@app.route('/')
def hello():

    url='https://account-d.docusign.com/oauth/auth'
    response_type="token"
    scope="signature"
    client_id="3d6303f3-6792-4a6a-86bf-df56834e740d"
    state="a39fh23hnf23"
    redirect_uri="http://localhost:5000/ds/callback"
    params={'response_type':'code','scope':"signature",'client_id':"3d6303f3-6792-4a6a-86bf-df56834e740d",'state':"a39fh23hnf23",'redirect_uri':"http://localhost:5000/ds/callback"}
    res=requests.get(url=url , params=params)
    print(res.text)
    return render_template(res.text)
    #return redirect(res.text)
    #return "Hello World!"

if __name__ == '__main__':
    app.run()